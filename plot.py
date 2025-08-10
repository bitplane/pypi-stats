"""Plotting utilities for PyPI download statistics"""
import plotext as plt

def plot_stacked_bars(labels, series, username):
    """Plot stacked bar chart of download statistics
    
    Args:
        labels: List of month labels (e.g. ['2024-01', '2024-02', ...])
        series: Dict mapping package names to download counts per month
        username: PyPI username for chart title
    """
    # Sort packages by total downloads (most popular first)
    totals = {p: sum(v) for p, v in series.items()}
    sorted_packages = sorted(series.keys(), key=lambda p: totals[p], reverse=True)
    series = {p: series[p] for p in sorted_packages}

    # plot stacked bars
    plt.clear_figure()
    plt.theme('dark')  # use dark theme for better colors
    plt.plotsize(120, 34)
    plt.title(f"PyPI downloads (last {len(labels)} full months) — {username}")
    plt.xlabel("Month")
    plt.ylabel("Downloads")
    plt.xticks(range(len(labels)), labels)

    # add each package as a stack
    # collect all series data for stacked_bar
    all_series = list(series.values())
    all_labels = list(series.keys())
    
    # use simple_stacked_bar for more color control
    plt.simple_stacked_bar(labels, all_series, labels=all_labels, width=100)
    plt.show()