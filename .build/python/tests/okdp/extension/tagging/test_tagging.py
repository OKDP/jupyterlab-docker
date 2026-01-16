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

from unittest.mock import patch

from tagging.manifests.spark_info import spark_info_manifest
from tagging.taggers import versions
from okdp.extension.tagging.apply_tags import Tagging
from okdp.extension.tagging.taggers import (
    LongTagger,
    scala_tagger,
    scala_major_minor_tagger,
    java_major_version_tagger,
    java_tagger,
    spark_tagger,
)

def test_java_tagger(mock_container, mock_exec_cmd):
    result = java_tagger(mock_container)
    assert result == "java-17.0.2"

def test_java_major_version_tagger(mock_container, mock_exec_cmd):
    """Test extracting major version from java_tagger."""
    result = java_major_version_tagger(mock_container)
    assert result == "java-17"


def test_scala_tagger(mock_container, mock_exec_cmd):
    """Test scala_tagger output."""
    result = scala_tagger(mock_container)
    assert result == "scala-2.13.12"

def test_scala_major_minor_tagger(mock_container, mock_exec_cmd):
    """Test scala_major_minor_tagger output."""
    minor = scala_major_minor_tagger(mock_container)
    assert minor == "scala-2.13"

def test_spark_tagger(mock_container, mock_exec_cmd):
    """Test spark_tagger output."""
    minor = spark_tagger(mock_container)
    assert minor == "spark-3.4.1"

def test_long_tagger(mock_container, mock_exec_cmd):
    long_tagger = LongTagger(spark_tagger, versions.python_major_minor_tagger, java_major_version_tagger, scala_major_minor_tagger)
    result = long_tagger.tag_value(mock_container)
    assert result == "spark-3.4.1-python-3.12-java-17-scala-2.13"

def test_generate_tags(mock_get_taggers_and_manifests, mock_container, mock_exec_cmd):
    """Test generate_tags output."""
    expected_tags = [
        "ghcr.io/owner/pyspark-notebook:2025-09-22-amd64",
        "ghcr.io/owner/pyspark-notebook:spark-3.4.1-python-3.12-java-17-scala-2.13-amd64",
        "ghcr.io/owner/pyspark-notebook:spark-3.4.1-python-3.12.3-java-17.0.2-scala-2.13.12-hub-4.0.1-lab-4.0.5-amd64",
    ]
    
    mock_get_taggers_and_manifests.return_value = (
        [
            LongTagger(spark_tagger, versions.python_major_minor_tagger, java_major_version_tagger, scala_major_minor_tagger),
            LongTagger(spark_tagger, versions.python_tagger, java_tagger, scala_tagger, versions.jupyter_hub_tagger, versions.jupyter_lab_tagger),
        ],
        [spark_info_manifest],
    )

    t = Tagging("pyspark-notebook:2025-09-22", "ghcr.io", "owner", "amd64")
    tags = t.generate_tags()

    assert tags[0] == "ghcr.io/owner/pyspark-notebook:2025-09-22-amd64"
    for tag in expected_tags:
      assert tag in tags
    assert len(tags) == len(expected_tags)

def test_apply_tags(mock_apply_tags_docker, mock_apply_tags_docker_runner, mock_get_taggers_and_manifests, mock_container):
    """Test apply_tags output."""
    class FakeTagger:
        def tag_value(self, container): return "tag1"

    mock_get_taggers_and_manifests.return_value = ([FakeTagger()], [])
    mock_apply_tags_docker_runner.return_value.__enter__.return_value = mock_container
    mock_apply_tags_docker_runner.return_value.__exit__.return_value = None

    t = Tagging("pyspark-notebook:2025-09-22", "ghcr.io", "owner", "arm64")
    t.apply_tags()

    # Check docker["tag", ...] was called with the right args
    docker_calls = [str(args) for args, _ in mock_apply_tags_docker.__getitem__.call_args_list]
    assert any("pyspark-notebook" in call for call in docker_calls)
    assert any("tag1" in call for call in docker_calls)

