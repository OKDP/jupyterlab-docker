# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

"""
* Add custom taggers (long form, scala etc taggers)
* Fix existing SparkVersionTagger when jdk '--add-opens' options are enabled for spark 3.2.x (java 11 compatibility)
* Unset JDK_JAVA_OPTIONS when asking for java program version
"""

from functools import cache

from docker.models.containers import Container

from tagging.docker_runner import DockerRunner

from tagging.taggers import *

@cache
def _get_program_version(container: Container, program: str) -> str:
    """"Get program version. Handle compatibility with spark 3.2.x/Java 11"""
    return DockerRunner.run_simple_command(container, cmd=f"/bin/sh -c 'unset JDK_JAVA_OPTIONS && {program} --version'")

def spark_version_prefix_line(cmd_output: str, search: str) -> int:
    for idx, line in enumerate(cmd_output.split("\n"), start=0):
      if line.find(search) != -1:
         return idx
    return -1

class SparkVersionTagger(TaggerInterface):
    @staticmethod
    def tag_value(container: Container) -> str:
        SPARK_VERSION_LINE_PREFIX = r"   /___/ .__/\_,_/_/ /_/\_\   version"
        spark_version = _get_program_version(container, "spark-submit")
        line = spark_version_prefix_line(spark_version, SPARK_VERSION_LINE_PREFIX)
        assert line > -1, f"Spark version line starting with '{SPARK_VERSION_LINE_PREFIX}' not found"
        version_line = spark_version.split("\n")[line]
        assert version_line.startswith(SPARK_VERSION_LINE_PREFIX), f"Spark version line '{version_line}' does not starts with '{SPARK_VERSION_LINE_PREFIX}'"
        return "spark-" + version_line.split(" ")[-1]

class ScalaMajorMinorVersionTagger(TaggerInterface):
    @staticmethod
    def tag_value(container: Container) -> str:
        full_version = ScalaVersionTagger.tag_value(container)
        return full_version[: full_version.rfind(".")]

class ScalaVersionTagger(TaggerInterface):
    @staticmethod
    def tag_value(container: Container) -> str:
        SCALA_VERSION_LINE_PREFIX = "Using Scala version"

        spark_version = _get_program_version(container, "spark-submit")
        line = spark_version_prefix_line(spark_version, SCALA_VERSION_LINE_PREFIX)
        assert line > -1, f"Spark version line starting with '{SCALA_VERSION_LINE_PREFIX}' not found"
        scala_version_line = spark_version.split("\n")[line]
        assert scala_version_line.startswith(SCALA_VERSION_LINE_PREFIX), f"Scala version line '{scala_version_line}' does not starts with '{SCALA_VERSION_LINE_PREFIX}'"
        return "scala-" + scala_version_line.split(" ")[3].split(",")[0]

class JavaVersionTagger(TaggerInterface):
    @staticmethod
    def tag_value(container: Container) -> str:
        return "java-" + _get_program_version(container, "java").split()[1]
    
class JavaMajorVersionTagger(TaggerInterface):
    @staticmethod
    def tag_value(container: Container) -> str:
        full_version = JavaVersionTagger.tag_value(container)
        return full_version[: full_version.find(".")]

class LongTagger(TaggerInterface):
    """ Long form tagger which combines all versions in a single tag """
    def __init__(self, *taggers: TaggerInterface):
       self.taggers = taggers
    
    def tag_value(self, container: Container) -> str:
        return "-".join((lambda taggers : (t.tag_value(container) for t in taggers))(self.taggers))
