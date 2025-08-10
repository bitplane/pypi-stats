#!/usr/bin/env python3
"""Convert ANSI terminal output to SVG using Rich"""
import sys
from rich.console import Console
from rich.text import Text

def ansi_to_svg(ansi_file, svg_file):
    """Convert ANSI file to SVG
    
    Args:
        ansi_file: Path to ANSI file
        svg_file: Output SVG path
    """
    # Read the ANSI content
    with open(ansi_file, 'r') as f:
        ansi_content = f.read()
    
    # Create a console to record the output
    console = Console(record=True, width=120, height=40, legacy_windows=False)
    
    # Print the ANSI content (Rich will interpret the ANSI codes)
    # Use no_wrap and overflow="ignore" to preserve exact spacing
    console.print(Text.from_ansi(ansi_content), overflow="ignore", crop=False, no_wrap=True)
    
    # Export to SVG
    svg = console.export_svg(title="PyPI Stats")
    
    # Write SVG
    with open(svg_file, 'w') as f:
        f.write(svg)
    
    print(f"SVG saved to {svg_file}", file=sys.stderr)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: ansi2svg.py input.ansi output.svg", file=sys.stderr)
        sys.exit(1)
    
    ansi_to_svg(sys.argv[1], sys.argv[2])