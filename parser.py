#!/usr/bin/env python3
# [project]
# name = "parser"
# requires-python = ">=3.8"
# dependencies = [
#     "unstructured[all-docs]",
#     "requests",
#     "rich"
# ]
# ///

import argparse
from pathlib import Path
from rich.console import Console
from unstructured.partition.auto import partition
from urllib.parse import urlparse
import os
import requests

console = Console()


def is_url(string):
    """Validate if a string is a URL."""
    try:
        result = urlparse(string)
        return all([result.scheme, result.netloc])
    except:
        return False


def process_document(source, strategy="fast"):
    """Process a document from URL or local file using specified strategy.

    Args:
        source (str): URL or file path to document
        strategy (str): One of 'fast', 'hires', 'ocr_only', 'auto'
    """
    if is_url(source):
        console.print(f"[blue]Downloading from URL: {source}[/blue]")
        response = requests.get(source)
        temp_file = Path("temp.pdf")
        temp_file.write_bytes(response.content)
        elements = partition(str(temp_file), strategy=strategy)
        temp_file.unlink()
    else:
        console.print(f"[blue]Processing local file: {source}[/blue]")
        elements = partition(source, strategy=strategy)

    return elements


def main():
    parser = argparse.ArgumentParser(description="Extract text from PDFs or URLs")
    parser.add_argument("source", help="PDF file path or URL")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument(
        "--strategy",
        "-s",
        help="Strategy to use for processing (fast, hires, ocr_only, auto)",
    )

    args = parser.parse_args()

    elements = process_document(args.source, args.strategy)

    # Output handling
    output = "\n".join([str(element) for element in elements])
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
    else:
        print(output)


if __name__ == "__main__":
    main()
