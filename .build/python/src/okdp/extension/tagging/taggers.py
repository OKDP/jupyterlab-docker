# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

"""
* Add custom taggers (long form, scala etc taggers)
* Fix existing SparkVersionTagger when jdk '--add-opens' options are enabled for spark 3.2.x (java 11 compatibility)
* Unset JDK_JAVA_OPTIONS when asking for java program version
"""

from functools import cache

from docker.models.containers import Container

from tagging.taggers.versions import java_tagger
from tagging.utils.docker_runner import DockerRunner

from tagging.taggers import *
from tagging.taggers.tagger_interface import TaggerInterface

@cache
def _get_program_version(container: Container, program: str) -> str:
    """"Get program version. Handle compatibility with spark 3.2.x/Java 11"""
    return DockerRunner.exec_cmd(container, cmd=f"/bin/sh -c 'unset JDK_JAVA_OPTIONS && {program} --version'")

def spark_version_prefix_line(cmd_output: str, search: str) -> int:
    for idx, line in enumerate(cmd_output.split("\n"), start=0):
      if line.find(search) != -1:
         return idx
    return -1

def spark_tagger(container: Container) -> str:
    SPARK_VERSION_LINE_PREFIX = r"   /___/ .__/\_,_/_/ /_/\_\   version"

    spark_version = _get_program_version(container, "spark-submit")
    version_line = next(
        filter(
            lambda line: line.startswith(SPARK_VERSION_LINE_PREFIX),
            spark_version.split("\n"),
        )
    )
    return "spark-" + version_line.split(" ")[-1]


def java_tagger(container: Container) -> str:
    return "java-" + _get_program_version(container, "java").split()[1]

def scala_major_minor_tagger(container: Container) -> str:
    full_version = scala_tagger(container)
    return full_version[: full_version.rfind(".")]

def scala_tagger(container: Container) -> str:
    SCALA_VERSION_LINE_PREFIX = "Using Scala version"

    spark_version = _get_program_version(container, "spark-submit")
    line = spark_version_prefix_line(spark_version, SCALA_VERSION_LINE_PREFIX)
    assert line > -1, f"Spark version line starting with '{SCALA_VERSION_LINE_PREFIX}' not found"
    scala_version_line = spark_version.split("\n")[line]
    assert scala_version_line.startswith(SCALA_VERSION_LINE_PREFIX), f"Scala version line '{scala_version_line}' does not starts with '{SCALA_VERSION_LINE_PREFIX}'"
    return "scala-" + scala_version_line.split(" ")[3].split(",")[0]

def java_major_version_tagger(container: Container) -> str:
    full_version = java_tagger(container)
    return full_version[: full_version.find(".")]

class LongTagger:
    """Combine multiple tagger functions into one long tag."""
    def __init__(self, *taggers: callable):
        self.taggers = taggers
    def tag_value(self, container: Container) -> str:
        return "-".join(tagger(container) for tagger in self.taggers)
