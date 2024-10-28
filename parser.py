#!/usr/bin/env python3
import argparse
import requests
from unstructured.partition.auto import partition
from urllib.parse import urlparse
import os


def is_url(string):
    try:
        result = urlparse(string)
        return all([result.scheme, result.netloc])
    except:
        return False


def process_document(source):
    if is_url(source):
        # Download PDF from URL
        response = requests.get(source)
        with open("temp.pdf", "wb") as f:
            f.write(response.content)
        elements = partition("temp.pdf")
        os.remove("temp.pdf")
    else:
        # Process local PDF
        elements = partition(source)

    return elements


def main():
    parser = argparse.ArgumentParser(description="Extract text from PDFs or URLs")
    parser.add_argument("source", help="PDF file path or URL")
    parser.add_argument("--output", "-o", help="Output file path")

    args = parser.parse_args()

    elements = process_document(args.source)

    # Output handling
    output = "\n".join([str(element) for element in elements])
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
    else:
        print(output)


if __name__ == "__main__":
    main()
