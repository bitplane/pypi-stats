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
    # Sort packages by total downloads (most popular first)
    totals = {p: sum(v) for p, v in series.items()}
    sorted_packages = sorted(series.keys(), key=lambda p: totals[p], reverse=True)
    series = {p: series[p] for p in sorted_packages}

    # Define colors and patterns for better visual distinction
    colors = ['red', 'green', 'blue', 'yellow', 'magenta', 'cyan', 'white', 
              'bright red', 'bright green', 'bright blue', 'bright yellow', 
              'bright magenta', 'bright cyan', 'orange', 'gray', 'purple']
    
    # Good working patterns - avoid solid blocks and ugly symbols
    patterns = ['█', '▄', '▌', '⠿', '■']  # solid, bottom-half, left-half, braille, square

    # plot stacked bars
    plt.clear_figure()
    plt.theme('dark')  # use dark theme for better colors
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
        
        color = colors[color_index]
        pattern = patterns[pattern_index % len(patterns)]
        
        # Add individual series with specific color and marker
        plt.stacked_bar(labels, [data], labels=[label], 
                       color=color, marker=pattern)
    
    plt.show()