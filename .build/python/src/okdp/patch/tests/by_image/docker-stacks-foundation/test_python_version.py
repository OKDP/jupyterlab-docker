# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

"""
Skip the hard check of python version to allow it's override at a build time:
--build-arg PYTHON_VERSION=3.x.x
""" 

import logging
import pytest  # type: ignore

from tests.conftest import TrackedContainer

LOGGER = logging.getLogger(__name__)
EXPECTED_PYTHON_VERSION = "3.11"

@pytest.mark.skip(reason="Allow override python version")
def test_python_version(container: TrackedContainer) -> None:
    LOGGER.info(
        f"Checking that python major.minor version is {EXPECTED_PYTHON_VERSION}"
    )
    logs = container.run_and_wait(
        timeout=10,
        command=["python", "--version"],
    )
    python = next(line for line in logs.splitlines() if line.startswith("Python "))
    full_version = python.split()[1]
    major_minor_version = full_version[: full_version.rfind(".")]

    assert major_minor_version == EXPECTED_PYTHON_VERSION

@pytest.mark.skip(reason="Allow override python version")
def test_python_pinned_version(container: TrackedContainer) -> None:
    LOGGER.info(f"Checking that pinned python version is {EXPECTED_PYTHON_VERSION}.*")
    logs = container.run_and_wait(
        timeout=10,
        command=["cat", "/opt/conda/conda-meta/pinned"],
    )
    assert f"python {EXPECTED_PYTHON_VERSION}.*" in logs
