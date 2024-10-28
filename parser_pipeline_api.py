#!/usr/bin/env python3
import os
from unstructured_ingest.v2.pipeline.pipeline import Pipeline
from unstructured_ingest.v2.interfaces import ProcessorConfig
from unstructured_ingest.v2.processes.connectors.local import (
    LocalIndexerConfig,
    LocalDownloaderConfig,
    LocalConnectionConfig,
    LocalUploaderConfig,
)


def process_documents(input_dir, output_dir):
    pipeline = Pipeline(
        processor_config=ProcessorConfig(
            strategy="fast"  # or "hires", "ocr_only", "auto"
        ),
        downloader_config=LocalDownloaderConfig(input_path=input_dir),
        indexer_config=LocalIndexerConfig(),
        uploader_config=LocalUploaderConfig(output_dir=output_dir),
    )
    pipeline.run()


if __name__ == "__main__":
    process_documents(".", "./output")
