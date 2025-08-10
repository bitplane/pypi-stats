#!/usr/bin/env python3
# BigQuery-based PyPI download stats
import argparse, datetime as dt, xmlrpc.client, sys, os, json
from collections import defaultdict
from pathlib import Path

from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv()

# Cache directory for monthly data
CACHE_DIR = Path("./cache")

def month_ends_last_full_month(n=12):
    """Return (months_labels, start_date, end_date) for last n full months."""
    today = dt.date.today()
    first_of_this_month = today.replace(day=1)
    end_date = first_of_this_month - dt.timedelta(days=1)           # last day of previous month
    # start at first day n-1 months before end_date's month
    month = end_date.replace(day=1)
    for _ in range(n - 1):
        month = (month.replace(day=1) - dt.timedelta(days=1)).replace(day=1)
    start_date = month
    # produce YYYY-MM labels from start .. end
    labels = []
    cur = start_date
    while cur <= end_date:
        labels.append(cur.strftime("%Y-%m"))
        # jump to next month
        next_month = (cur.replace(day=28) + dt.timedelta(days=4)).replace(day=1)
        cur = next_month
    return labels, start_date.isoformat(), end_date.isoformat()

def user_projects(username: str):
    s = xmlrpc.client.ServerProxy("https://pypi.org/pypi")
    return sorted({pkg for _, pkg in s.user_packages(username)})

def fetch_single_month_stats(project_id: str, projects, year_month: str, dry_run=False):
    """Fetch stats for a single month (YYYY-MM format)"""
    client = bigquery.Client(project=project_id)
    
    # Parse year-month and create date range for the full month
    year, month = map(int, year_month.split('-'))
    start_date = dt.date(year, month, 1)
    
    # Get last day of month
    if month == 12:
        end_date = dt.date(year + 1, 1, 1) - dt.timedelta(days=1)
    else:
        end_date = dt.date(year, month + 1, 1) - dt.timedelta(days=1)
    
    sql = """
    SELECT
      project,
      COUNT(1) AS downloads
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE project IN UNNEST(@projects)
      AND DATE(timestamp) BETWEEN @start AND @end
    GROUP BY project
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ArrayQueryParameter("projects", "STRING", projects),
            bigquery.ScalarQueryParameter("start", "DATE", start_date.isoformat()),
            bigquery.ScalarQueryParameter("end", "DATE", end_date.isoformat()),
        ],
        dry_run=dry_run,
        use_query_cache=True
    )
    
    job = client.query(sql, job_config=job_config, location="US")
    
    if dry_run:
        print(f"Query for {year_month} will process {job.total_bytes_processed / (1024**3):.2f} GB", file=sys.stderr)
        return []
    
    # Return as dict for easier caching
    return {row["project"]: row["downloads"] for row in job}

def get_cached_month_data(username: str, year_month: str):
    """Load cached data for a month, returns None if not cached"""
    user_cache_dir = CACHE_DIR / username
    cache_file = user_cache_dir / f"{year_month}.json"
    if cache_file.exists():
        with open(cache_file) as f:
            return json.load(f)
    return None

def save_month_data_to_cache(username: str, year_month: str, data):
    """Save month data to cache"""
    user_cache_dir = CACHE_DIR / username
    user_cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = user_cache_dir / f"{year_month}.json"
    with open(cache_file, 'w') as f:
        json.dump(data, f, indent=2)

def monthly_stats_generator(project_id: str, username: str, projects, months_list, dry_run=False):
    """Generator that yields (month, stats_dict) for each month"""
    current_month = dt.date.today().strftime("%Y-%m")
    
    for month in months_list:
        # Check if we need to query BigQuery
        need_query = (
            month == current_month or  # Always refresh current month
            get_cached_month_data(username, month) is None  # No cached data
        )
        
        if need_query:
            print(f"Querying BigQuery for {month}...", file=sys.stderr)
            if dry_run:
                try:
                    fetch_single_month_stats(project_id, projects, month, dry_run=True)
                except Exception as e:
                    print(f"ERROR: Failed to query {month}: {e}", file=sys.stderr)
                yield month, {}
            else:
                try:
                    stats = fetch_single_month_stats(project_id, projects, month)
                    save_month_data_to_cache(username, month, stats)
                    yield month, stats
                except Exception as e:
                    print(f"ERROR: Failed to query {month}: {e}", file=sys.stderr)
                    print(f"Skipping {month} - run again later when quota resets", file=sys.stderr)
                    yield month, {}
        else:
            print(f"Using cached data for {month}", file=sys.stderr)
            cached_data = get_cached_month_data(username, month)
            yield month, cached_data

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("username")
    ap.add_argument("--project", help="GCP project id (defaults to GCP_PROJECT env var)")
    ap.add_argument("--months", type=int, default=12, help="last N full months (default 12)")
    ap.add_argument("--min-total", type=int, default=0, help="hide packages with total < N")
    ap.add_argument("--dry-run", action="store_true", help="show query cost without running")
    args = ap.parse_args()

    project_id = args.project or os.getenv("GCP_PROJECT")
    if not project_id:
        print("Error: No GCP project specified. Use --project or set GCP_PROJECT environment variable.")
        sys.exit(1)

    labels, start_date, end_date = month_ends_last_full_month(args.months)
    pkgs = user_projects(args.username)
    if not pkgs:
        print("No packages for that user.")
        sys.exit(0)

    # Build matrix using cached monthly data
    series = {p: [0] * len(labels) for p in pkgs}
    
    # Use generator to get data month by month
    for i, (month, month_data) in enumerate(monthly_stats_generator(project_id, args.username, pkgs, labels, dry_run=args.dry_run)):
        if args.dry_run:
            continue
            
        # Fill in download counts for this month
        for project, downloads in month_data.items():
            if project in series:
                series[project][i] = downloads
    
    if args.dry_run:
        return

    # optionally drop low-traffic packages (keeps chart readable)
    totals = {p: sum(v) for p, v in series.items()}
    if args.min_total > 0:
        series = {p: v for p, v in series.items() if totals[p] >= args.min_total}
        if not series:
            print("All packages filtered out by --min-total.")
            sys.exit(0)

    # Import and use plotting module
    from plot import plot_stacked_bars
    plot_stacked_bars(labels, series, args.username)

if __name__ == "__main__":
    main()