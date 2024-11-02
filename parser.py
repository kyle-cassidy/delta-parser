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


def process_document(source, strategy="hi_res"):
    """Process a document from URL, local file, or directory using specified strategy.

    Args:
        source (str): URL, file path, or directory path
        strategy (str): One of 'fast', 'hi_res', 'ocr_only', 'auto'
    Returns:
        dict: JSON formatted extraction results
    """
    if is_url(source):
        console.print(f"[blue]Downloading from URL: {source}[/blue]")
        response = requests.get(source)
        temp_file = Path("temp.pdf")
        temp_file.write_bytes(response.content)
        elements = partition(str(temp_file), strategy=strategy)
        temp_file.unlink()
    else:
        source_path = Path(source)
        if source_path.is_dir():
            console.print(f"[blue]Processing directory: {source}[/blue]")
            elements = []
            # Full list of supported extensions from Unstructured docs
            supported_extensions = [
                ".bmp",
                ".csv",
                ".doc",
                ".docx",
                ".eml",
                ".epub",
                ".heic",
                ".html",
                ".jpeg",
                ".png",
                ".md",
                ".msg",
                ".odt",
                ".org",
                ".p7s",
                ".pdf",
                ".png",
                ".ppt",
                ".pptx",
                ".rst",
                ".rtf",
                ".tiff",
                ".txt",
                ".tsv",
                ".xls",
                ".xlsx",
                ".xml",
            ]

            for file in source_path.rglob("*"):
                if file.suffix.lower() in supported_extensions:
                    console.print(f"[cyan]Processing file: {file}[/cyan]")
                    try:
                        file_elements = partition(str(file), strategy=strategy)
                        elements.extend(file_elements)
                    except Exception as e:
                        console.print(f"[red]Error processing {file}: {str(e)}[/red]")
        else:
            console.print(f"[blue]Processing local file: {source}[/blue]")
            elements = partition(source, strategy=strategy)

    # Enhanced JSON structure for form-like content
    output = []
    current_key = None

    for element in elements:
        text = str(element)
        element_type = element.__class__.__name__

        # Convert metadata to dict if it exists
        metadata = {}
        if hasattr(element, "metadata"):
            metadata = {
                k: str(v)
                for k, v in element.metadata.__dict__.items()
                if not k.startswith("_")
            }

        # Basic form field detection
        if ":" in text:
            key, value = text.split(":", 1)  # Split on first occurrence of ":"
            output.append(
                {
                    "type": "form_field",
                    "key": key.strip(),
                    "value": value.strip(),
                    "metadata": metadata,
                }
            )
        else:
            output.append({"type": element_type, "text": text, "metadata": metadata})

    return output


def main():
    parser = argparse.ArgumentParser(description="Extract text from PDFs or URLs")
    parser.add_argument("source", help="PDF file path or URL")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument(
        "--strategy",
        "-s",
        choices=["fast", "hi_res", "ocr_only", "auto"],
        default="hi_res",
        help="Strategy to use for processing (fast, hi_res, ocr_only, auto).",
    )

    args = parser.parse_args()
    elements = process_document(args.source, args.strategy)

    # Output handling
    if args.output:
        import json

        with open(args.output, "w") as f:
            json.dump({"elements": elements}, f, indent=2)
        console.print(f"[green]Output written to: {args.output}[/green]")
    else:
        import json

        print(json.dumps({"elements": elements}, indent=2))


if __name__ == "__main__":
    main()
