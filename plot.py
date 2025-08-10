"""Plotting utilities for PyPI download statistics"""
import plotext as plt
import sys

def plot_stacked_bars(labels, series, username):
    """Plot stacked bar chart with colors and patterns for better distinction
    
    Args:
        labels: List of month labels (e.g. ['2024-01', '2024-02', ...])
        series: Dict mapping package names to download counts per month
        username: PyPI username for chart title
    """
    # Filter out packages with zero downloads and sort by total downloads
    totals = {p: sum(v) for p, v in series.items()}
    # Remove packages with 0 total downloads
    filtered_packages = {p: total for p, total in totals.items() if total > 0}
    sorted_packages = sorted(filtered_packages.keys(), key=lambda p: totals[p], reverse=True)
    series = {p: series[p] for p in sorted_packages}
    
    print(f"Showing {len(sorted_packages)} packages with downloads (filtered out {len(totals) - len(sorted_packages)} zero-download packages)", file=sys.stderr)

    # Use basic ANSI colors 1-8 (skip 0=black) plus hand-picked good colors
    # 1=red, 2=green, 3=yellow, 4=blue, 5=magenta, 6=cyan, 7=white, 8=gray
    colors = list(range(1, 9)) + [82, 52, 213]  # Basic colors + selected extras
    
    patterns = ['▌', '⯀', '█']

    # plot stacked bars
    plt.clear_figure()
    plt.theme('dark')  # use dark theme for better colors
    plt.limit_size(False, False)  # Don't limit to terminal size (important for pipes)
    plt.plotsize(120, 34)
    plt.title(f"PyPI downloads (last {len(labels)} full months) — {username}")
    plt.xlabel("Month")
    plt.ylabel("Downloads")
    plt.xticks(range(len(labels)), labels)

    # Add each package individually with color and pattern cycling
    all_series = list(series.values())
    all_labels = list(series.keys())
    
    for i, (label, data) in enumerate(zip(all_labels, all_series)):
        # First cycle through all colors with solid pattern, then repeat colors with next pattern
        color_index = i % len(colors)
        pattern_index = i // len(colors)  # Only advance pattern after all colors used
        
        color = colors[color_index]  # Get the integer color code
        pattern = patterns[pattern_index % len(patterns)]
        
        # Add individual series with specific color and marker
        # Pass color as a list since stacked_bar expects a list
        plt.stacked_bar(labels, [data], labels=[label], 
                       color=[color], marker=pattern)
    
    plt.show()
