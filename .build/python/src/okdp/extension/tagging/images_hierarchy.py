# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

"""
Extension of the original file:
* Remove simple form taggers (date_tagger/commit_sha_tagger, etc) which may conflicts with multiple python version built on the same date
* Add long form tagger to uniquely identify an image
* Remove the dependency for pyspark-notebook to parent images tags
"""

from dataclasses import dataclass, field

from tagging.manifests.apt_packages import apt_packages_manifest
from tagging.manifests.conda_environment import conda_environment_manifest
from tagging.manifests.julia_packages import julia_packages_manifest
from tagging.manifests.manifest_interface import ManifestInterface
from tagging.manifests.r_packages import r_packages_manifest
from tagging.manifests.spark_info import spark_info_manifest

from tagging.taggers import versions
from tagging.taggers.date import date_tagger
from tagging.taggers.sha import commit_sha_tagger
from tagging.taggers.tagger_interface import TaggerInterface
from tagging.taggers.ubuntu_version import ubuntu_version_tagger

from okdp.extension.tagging.taggers import (
    java_tagger,
    spark_tagger,
    java_major_version_tagger,
    scala_tagger,
    scala_major_minor_tagger,
    LongTagger,
)

@dataclass
class ImageDescription:
    parent_image: str | None
    taggers: list[TaggerInterface] = field(default_factory=list)
    manifests: list[ManifestInterface] = field(default_factory=list)


ALL_IMAGES = {
    "docker-stacks-foundation": ImageDescription(
        parent_image=None,
        taggers=[
            LongTagger(ubuntu_version_tagger, versions.python_tagger),
            LongTagger(versions.python_tagger, commit_sha_tagger),
            LongTagger(versions.python_tagger, commit_sha_tagger),
            LongTagger(versions.python_tagger, date_tagger),
            LongTagger(versions.python_major_minor_tagger, date_tagger),
        ],
        manifests=[conda_environment_manifest, apt_packages_manifest],
    ),
    "base-notebook": ImageDescription(
        parent_image="docker-stacks-foundation",
        taggers=[
            LongTagger(versions.python_tagger, versions.jupyter_hub_tagger, versions.jupyter_lab_tagger),
            LongTagger(versions.python_tagger, versions.jupyter_hub_tagger, versions.jupyter_lab_tagger, date_tagger),
        ],
    ),
    "minimal-notebook": ImageDescription(parent_image="base-notebook"),
    "scipy-notebook": ImageDescription(parent_image="minimal-notebook"),
    "r-notebook": ImageDescription(
        parent_image="minimal-notebook",
        taggers=[
            LongTagger(versions.python_tagger, versions.r_tagger),
            LongTagger(versions.python_tagger, versions.r_tagger, date_tagger),
            LongTagger(versions.python_tagger, versions.r_tagger, versions.jupyter_hub_tagger, versions.jupyter_lab_tagger),
            LongTagger(versions.python_tagger, versions.r_tagger, versions.jupyter_hub_tagger, versions.jupyter_lab_tagger, date_tagger),
        ],
        manifests=[r_packages_manifest],
    ),
    "julia-notebook": ImageDescription(
        parent_image="minimal-notebook",
        taggers=[
            LongTagger(versions.python_tagger, versions.julia_tagger),
            LongTagger(versions.python_tagger, versions.julia_tagger, date_tagger),
            LongTagger(versions.python_tagger, versions.julia_tagger, versions.jupyter_hub_tagger, versions.jupyter_lab_tagger),
            LongTagger(versions.python_tagger, versions.julia_tagger, versions.jupyter_hub_tagger, versions.jupyter_lab_tagger, date_tagger),
        ],
        manifests=[julia_packages_manifest],
    ),
    "tensorflow-notebook": ImageDescription(
        parent_image="scipy-notebook", 
        taggers=[
            LongTagger(versions.python_tagger, versions.tensorflow_tagger),
            LongTagger(versions.python_tagger, versions.tensorflow_tagger, date_tagger),
            LongTagger(versions.python_tagger, versions.tensorflow_tagger, versions.jupyter_hub_tagger, versions.jupyter_lab_tagger),
            LongTagger(versions.python_tagger, versions.tensorflow_tagger, versions.jupyter_hub_tagger, versions.jupyter_lab_tagger, date_tagger),
        ]
    ),
    "pytorch-notebook": ImageDescription(
        parent_image="scipy-notebook", 
        taggers=[
            LongTagger(versions.python_tagger, versions.pytorch_tagger),
            LongTagger(versions.python_tagger, versions.pytorch_tagger, date_tagger),
            LongTagger(versions.python_tagger, versions.pytorch_tagger, versions.jupyter_hub_tagger, versions.jupyter_lab_tagger),
            LongTagger(versions.python_tagger, versions.pytorch_tagger, versions.jupyter_hub_tagger, versions.jupyter_lab_tagger, date_tagger),
        ]
    ),
    "datascience-notebook": ImageDescription(
        parent_image="scipy-notebook",
        taggers=[
            LongTagger(versions.python_tagger, versions.r_tagger, versions.julia_tagger),
            LongTagger(versions.python_tagger, versions.r_tagger, versions.julia_tagger, date_tagger),
            LongTagger(versions.python_tagger, versions.r_tagger, versions.julia_tagger, versions.jupyter_hub_tagger, versions.jupyter_lab_tagger),
            LongTagger(versions.python_tagger, versions.r_tagger, versions.julia_tagger, versions.jupyter_hub_tagger, versions.jupyter_lab_tagger, date_tagger),
        ],
        manifests=[r_packages_manifest, julia_packages_manifest],
    ),
    "pyspark-notebook": ImageDescription(
        parent_image="scipy-notebook",
        taggers=[
            LongTagger(spark_tagger, versions.python_major_minor_tagger, java_major_version_tagger, scala_major_minor_tagger),
            LongTagger(spark_tagger, versions.python_major_minor_tagger, java_major_version_tagger, scala_major_minor_tagger, commit_sha_tagger),
            LongTagger(spark_tagger, versions.python_major_minor_tagger, java_major_version_tagger, scala_major_minor_tagger, date_tagger),
            LongTagger(spark_tagger, versions.python_tagger, java_tagger, scala_tagger, versions.jupyter_hub_tagger, versions.jupyter_lab_tagger),
            LongTagger(spark_tagger, versions.python_tagger, java_tagger, scala_tagger, versions.jupyter_hub_tagger, versions.jupyter_lab_tagger, date_tagger),
            ],
        manifests=[spark_info_manifest],
    ),
    "all-spark-notebook": ImageDescription(
        parent_image="pyspark-notebook",
        taggers=[
            LongTagger(spark_tagger, versions.python_tagger, versions.r_tagger, java_tagger, scala_tagger, versions.jupyter_hub_tagger, versions.jupyter_lab_tagger),
            LongTagger(spark_tagger, versions.python_tagger, versions.r_tagger, java_tagger, scala_tagger, versions.jupyter_hub_tagger, versions.jupyter_lab_tagger, date_tagger),
        ],
        manifests=[r_packages_manifest],
    ),
}
