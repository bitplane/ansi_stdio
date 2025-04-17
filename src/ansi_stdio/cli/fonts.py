#!/usr/bin/env python3
"""
List available monospace fonts.

Usage:
    monospace-fonts [--print=FIELD] [--format=FORMAT]

Options:
    --print FIELD     What to print. Can be 'name', 'path', or 'all' [default: name]
    --format FORMAT   Output format. Can be 'text', 'json', or 'csv' [default: text]
    -h, --help        Show this help message
"""

import argparse
import csv
import json
import sys

from ..utils.fonts import get_monospace_fonts


def main():
    """Entry point for the CLI script."""
    parser = argparse.ArgumentParser(description="List available monospace fonts.")
    parser.add_argument(
        "--print",
        choices=["name", "path", "all"],
        default="name",
        help="What to print (name, path, or all)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json", "csv"],
        default="text",
        help="Output format (text, json, or csv)",
    )

    args = parser.parse_args()

    try:
        fonts = get_monospace_fonts()

        # Handle different output formats
        if args.format == "text":
            print_text_output(fonts, args.print)
        elif args.format == "json":
            print_json_output(fonts, args.print)
        elif args.format == "csv":
            print_csv_output(fonts, args.print)

        return 0

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1


def print_text_output(fonts, print_field):
    """Print fonts in text format."""
    if not fonts:
        print("No monospace fonts found.")
        return

    for name, path in fonts.items():
        if print_field == "name":
            print(name)
        elif print_field == "path":
            print(path)
        else:  # all
            print(f"{name}: {path}")


def print_json_output(fonts, print_field):
    """Print fonts in JSON format."""
    result = {}

    if print_field == "name":
        result = list(fonts.keys())
    elif print_field == "path":
        result = list(fonts.values())
    else:  # all
        result = fonts

    print(json.dumps(result, indent=2))


def print_csv_output(fonts, print_field):
    """Print fonts in CSV format."""
    writer = csv.writer(sys.stdout)

    # Write header
    if print_field == "name":
        writer.writerow(["Font Name"])
    elif print_field == "path":
        writer.writerow(["Font Path"])
    else:  # all
        writer.writerow(["Font Name", "Font Path"])

    # Write data
    for name, path in fonts.items():
        if print_field == "name":
            writer.writerow([name])
        elif print_field == "path":
            writer.writerow([path])
        else:  # all
            writer.writerow([name, path])


if __name__ == "__main__":
    sys.exit(main())
