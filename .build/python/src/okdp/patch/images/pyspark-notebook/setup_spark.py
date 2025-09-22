#!/usr/bin/env python3
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

# Requirements:
# - Run as the root user
# - Required env variable: SPARK_HOME

"""
Downloads and unpacks Spark.
The resulting Spark directory name is returned.

Modification:
- Handles Spark tarballs hosted on GitHub releases.
  If `spark_download_url` points to GitHub (contains "https://github.com"), the
  tarball is expected directly at `{spark_download_url}/{spark_dir_name}.tgz`.
  Otherwise, falls back to Apache-style archive structure:
  `{spark_download_url}/spark-{spark_version}/{spark_dir_name}.tgz`.
- This allows using GitHub releases for faster downloads instead of the Apache archive.
"""

import argparse
import logging
import os
import re
import subprocess
from pathlib import Path

import requests
from bs4 import BeautifulSoup

LOGGER = logging.getLogger(__name__)


def get_all_refs(url: str) -> list[str]:
    """
    Get all the references for a given webpage
    """
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    return [a["href"] for a in soup.find_all("a", href=True)]


def get_latest_spark_version() -> str:
    """
    Returns the last version of Spark using spark archive
    """
    LOGGER.info("Downloading Spark versions information")
    all_refs = get_all_refs("https://archive.apache.org/dist/spark/")
    LOGGER.info(f"All refs: {all_refs}")
    pattern = re.compile(r"^spark-(\d+\.\d+\.\d+)/$")
    versions = [match.group(1) for ref in all_refs if (match := pattern.match(ref))]
    LOGGER.info(f"Available versions: {versions}")

    # Compare versions semantically
    def version_array(ver: str) -> tuple[int, int, int, str]:
        # 3.5.3 -> [3, 5, 3, ""]
        # 4.0.0-preview2 -> [4, 0, 0, "preview2"]
        arr = ver.split(".")
        assert len(arr) == 3, arr
        major, minor = int(arr[0]), int(arr[1])
        patch, _, preview = arr[2].partition("-")
        return (major, minor, int(patch), preview)

    latest_version = max(versions, key=lambda ver: version_array(ver))
    LOGGER.info(f"Latest version: {latest_version}")
    return latest_version


def download_spark(
    *,
    spark_version: str,
    hadoop_version: str,
    scala_version: str,
    spark_download_url: Path,
) -> str:
    """
    Downloads and unpacks spark
    The resulting spark directory name is returned
    """
    LOGGER.info("Downloading and unpacking Spark")
    spark_dir_name = f"spark-{spark_version}-bin-hadoop{hadoop_version}"
    if scala_version:
        spark_dir_name += f"-scala{scala_version}"
    LOGGER.info(f"Spark directory name: {spark_dir_name}")
    # spark_url = spark_download_url / f"spark-{spark_version}" / f"{spark_dir_name}.tgz"
    # Determine URL based on source
    # Note the bug in argument spark_download_url: Path (should be str)
    if "https:/github.com" in str(spark_download_url):
        spark_url = spark_download_url / f"{spark_dir_name}.tgz"
    else:
        spark_url = spark_download_url / f"spark-{spark_version}" / f"{spark_dir_name}.tgz"

    LOGGER.info(f"Spark Download URL: {spark_url}")

    tmp_file = Path("/tmp/spark.tar.gz")
    subprocess.check_call(
        ["curl", "--progress-bar", "--location", "--output", tmp_file, spark_url]
    )
    subprocess.check_call(
        [
            "tar",
            "xzf",
            tmp_file,
            "-C",
            "/usr/local",
            "--owner",
            "root",
            "--group",
            "root",
            "--no-same-owner",
        ]
    )
    tmp_file.unlink()
    return spark_dir_name


def configure_spark(spark_dir_name: str, spark_home: Path) -> None:
    """
    Creates a ${SPARK_HOME} symlink to a versioned spark directory
    Creates a 10spark-config.sh symlink to source PYTHONPATH automatically
    """
    LOGGER.info("Configuring Spark")
    subprocess.check_call(["ln", "-s", f"/usr/local/{spark_dir_name}", spark_home])

    # Add a link in the before_notebook hook in order to source PYTHONPATH automatically
    CONFIG_SCRIPT = "/usr/local/bin/before-notebook.d/10spark-config.sh"
    subprocess.check_call(
        ["ln", "-s", spark_home / "sbin/spark-config.sh", CONFIG_SCRIPT]
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--spark-version", required=True)
    arg_parser.add_argument("--hadoop-version", required=True)
    arg_parser.add_argument("--scala-version", required=True)
    arg_parser.add_argument("--spark-download-url", type=Path, required=True)
    args = arg_parser.parse_args()

    args.spark_version = args.spark_version or get_latest_spark_version()

    spark_dir_name = download_spark(
        spark_version=args.spark_version,
        hadoop_version=args.hadoop_version,
        scala_version=args.scala_version,
        spark_download_url=args.spark_download_url,
    )
    configure_spark(
        spark_dir_name=spark_dir_name, spark_home=Path(os.environ["SPARK_HOME"])
    )
