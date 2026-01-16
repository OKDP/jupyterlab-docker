#
# Copyright 2026 The OKDP Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from unittest.mock import MagicMock, patch
import pytest

# ------------------------------
# Patch docker.from_env and plumbum.local["docker"] before any import
# ------------------------------
mock_docker_client = MagicMock()
patcher = patch("docker.from_env", return_value=mock_docker_client)
patcher.start()

mock_docker_cmd = MagicMock()
patcher_plumbum = patch("plumbum.local", return_value={"docker": mock_docker_cmd})
patcher_plumbum.start()

@pytest.fixture
def mock_container():
    """Fake docker container object"""
    container = MagicMock()
    container.name = "mock_container"

    exec_result = MagicMock()
    exec_result.exit_code = 0
    exec_result.output = b""
    container.exec_run.return_value = exec_result

    return container


@pytest.fixture
def mock_docker_runner(mock_container):
    """Patch DockerRunner context manager"""
    with patch("tagging.utils.docker_runner.DockerRunner") as MockRunner:
        instance = MockRunner.return_value
        instance.__enter__.return_value = mock_container
        instance.__exit__.return_value = None
        instance.exec_cmd.side_effect = lambda c, cmd: f"Executed {cmd}"
        yield MockRunner


@pytest.fixture
def mock_exec_cmd():
    """Patch DockerRunner.exec_cmd with command-based return values"""
    def fake_exec_cmd(container, cmd: str) -> str:
        if "java" in cmd:
            return 'openjdk 17.0.2 2022-01-18'
        elif "python" in cmd:
            return "Python 3.12.3"
        elif "scala" in cmd:
            return "Using Scala version 2.13.8, compiled blah"
        elif "mamba" in cmd:
            return "0.27.0"
        elif "conda" in cmd:
            return "conda 23.5.0"
        elif "jupyter-notebook" in cmd:
            return "6.5.4"
        elif "jupyter-lab" in cmd:
            return "4.0.5"
        elif "jupyterhub" in cmd:
            return "4.0.1"
        elif "R" in cmd:
            return "R version 4.3.1 (2023-06-16)"
        elif "julia" in cmd:
            return "julia version 1.9.2"
        elif "spark-submit" in cmd:
            return r"""Welcome to
      ____              __
     / __/__  ___ _____/ /__
    _\ \/ _ \/ _ `/ __/  '_/
   /___/ .__/\_,_/_/ /_/\_\   version 3.4.1
      /_/

Using Scala version 2.13.12, OpenJDK 64-Bit Server VM, 17.0.2
Branch HEAD
Compiled by user heartsavior on 2024-02-15T11:24:58Z
Revision fd86f85e181fc2dc0f50a096855acf83a6cc5d9c
Url https://github.com/apache/spark
Type --help for more information."""
        else:
            return "error output"

    with patch("tagging.utils.docker_runner.DockerRunner.exec_cmd", side_effect=fake_exec_cmd) as mock_exec:
        yield mock_exec

@pytest.fixture
def mock_get_taggers_and_manifests():
    """
    Fixture to patch `get_taggers_and_manifests` inside `apply_tags.py`.

    This ensures tests don't depend on the real ALL_IMAGES mapping
    and can provide controlled taggers/manifests for Tagging.generate_tags()
    or Tagging.apply_tags().
    """
    with patch("okdp.extension.tagging.apply_tags.get_taggers_and_manifests") as mock_get:
        yield mock_get

@pytest.fixture
def mock_apply_tags_docker_runner(mock_container):
    """Patch apply_tags.DockerRunner context manager."""
    with patch("okdp.extension.tagging.apply_tags.DockerRunner") as MockRunner:
        instance = MockRunner.return_value
        instance.__enter__.return_value = mock_container
        instance.__exit__.return_value = None
        yield MockRunner

@pytest.fixture
def mock_apply_tags_docker():
    """Patch apply_tags.docker (plumbum.local['docker'])."""
    with patch("okdp.extension.tagging.apply_tags.docker") as mock_docker:
        yield mock_docker
