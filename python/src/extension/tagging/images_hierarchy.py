# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

"""
Extension of the original file:
* Remove simple form taggers (DateTagger/SHATagger, etc) which may conflicts with multiple python version built on the same date
* Add long form tagger to uniquely identify an image
* Remove the dependency for pyspark-notebook to parent images tags
"""

from dataclasses import dataclass, field
from typing import Optional
from extension.tagging.taggers import (
    JavaMajorVersionTagger,
    JavaVersionTagger,
    LongTagger,
    SparkVersionTagger,
    ScalaVersionTagger,
    ScalaMajorMinorVersionTagger,
)

from tagging.manifests import (
    AptPackagesManifest,
    CondaEnvironmentManifest,
    JuliaPackagesManifest,
    ManifestInterface,
    RPackagesManifest,
    SparkInfoManifest,
)
from tagging.taggers import (
    DateTagger,
    JuliaVersionTagger,
    JupyterHubVersionTagger,
    JupyterLabVersionTagger,
    PythonMajorMinorVersionTagger,
    PythonVersionTagger,
    PytorchVersionTagger,
    RVersionTagger,
    SHATagger,
    TaggerInterface,
    TensorflowVersionTagger,
    UbuntuVersionTagger,
)


@dataclass
class ImageDescription:
    parent_image: Optional[str]
    taggers: list[TaggerInterface] = field(default_factory=list)
    manifests: list[ManifestInterface] = field(default_factory=list)


ALL_IMAGES = {
    "docker-stacks-foundation": ImageDescription(
        parent_image=None,
        taggers=[
            LongTagger(UbuntuVersionTagger(), PythonVersionTagger()),
            LongTagger(PythonVersionTagger(), SHATagger()),
            LongTagger(PythonVersionTagger(), SHATagger()),
            LongTagger(PythonVersionTagger(), DateTagger()),
            LongTagger(PythonMajorMinorVersionTagger(), DateTagger()),
        ],
        manifests=[CondaEnvironmentManifest(), AptPackagesManifest()],
    ),
    "base-notebook": ImageDescription(
        parent_image="docker-stacks-foundation",
        taggers=[
            LongTagger(PythonVersionTagger(), JupyterHubVersionTagger(), JupyterLabVersionTagger()),
            LongTagger(PythonVersionTagger(), JupyterHubVersionTagger(), JupyterLabVersionTagger(), DateTagger()),
        ],
    ),
    "minimal-notebook": ImageDescription(parent_image="base-notebook"),
    "scipy-notebook": ImageDescription(parent_image="minimal-notebook"),
    "r-notebook": ImageDescription(
        parent_image="minimal-notebook",
        taggers=[
            LongTagger(PythonVersionTagger(), RVersionTagger()),
            LongTagger(PythonVersionTagger(), RVersionTagger(), DateTagger()),
            LongTagger(PythonVersionTagger(), RVersionTagger(), JupyterHubVersionTagger(), JupyterLabVersionTagger()),
            LongTagger(PythonVersionTagger(), RVersionTagger(), JupyterHubVersionTagger(), JupyterLabVersionTagger(), DateTagger()),
        ],
        manifests=[RPackagesManifest()],
    ),
    "julia-notebook": ImageDescription(
        parent_image="minimal-notebook",
        taggers=[
            LongTagger(PythonVersionTagger(), JuliaVersionTagger()),
            LongTagger(PythonVersionTagger(), JuliaVersionTagger(), DateTagger()),
            LongTagger(PythonVersionTagger(), JuliaVersionTagger(), JupyterHubVersionTagger(), JupyterLabVersionTagger()),
            LongTagger(PythonVersionTagger(), JuliaVersionTagger(), JupyterHubVersionTagger(), JupyterLabVersionTagger(), DateTagger()),
        ],
        manifests=[JuliaPackagesManifest()],
    ),
    "tensorflow-notebook": ImageDescription(
        parent_image="scipy-notebook", 
        taggers=[
            LongTagger(PythonVersionTagger(), TensorflowVersionTagger()),
            LongTagger(PythonVersionTagger(), TensorflowVersionTagger(), DateTagger()),
            LongTagger(PythonVersionTagger(), TensorflowVersionTagger(), JupyterHubVersionTagger(), JupyterLabVersionTagger()),
            LongTagger(PythonVersionTagger(), TensorflowVersionTagger(), JupyterHubVersionTagger(), JupyterLabVersionTagger(), DateTagger()),
        ]
    ),
    "pytorch-notebook": ImageDescription(
        parent_image="scipy-notebook", 
        taggers=[
            LongTagger(PythonVersionTagger(), PytorchVersionTagger()),
            LongTagger(PythonVersionTagger(), PytorchVersionTagger(), DateTagger()),
            LongTagger(PythonVersionTagger(), PytorchVersionTagger(), JupyterHubVersionTagger(), JupyterLabVersionTagger()),
            LongTagger(PythonVersionTagger(), PytorchVersionTagger(), JupyterHubVersionTagger(), JupyterLabVersionTagger(), DateTagger()),
        ]
    ),
    "datascience-notebook": ImageDescription(
        parent_image="scipy-notebook",
        taggers=[
            LongTagger(PythonVersionTagger(), RVersionTagger(), JuliaVersionTagger()),
            LongTagger(PythonVersionTagger(), RVersionTagger(), JuliaVersionTagger(), DateTagger()),
            LongTagger(PythonVersionTagger(), RVersionTagger(), JuliaVersionTagger(), JupyterHubVersionTagger(), JupyterLabVersionTagger()),
            LongTagger(PythonVersionTagger(), RVersionTagger(), JuliaVersionTagger(), JupyterHubVersionTagger(), JupyterLabVersionTagger(), DateTagger()),
        ],
        manifests=[RPackagesManifest(), JuliaPackagesManifest()],
    ),
    "pyspark-notebook": ImageDescription(
        parent_image=None,
        taggers=[
            LongTagger(SparkVersionTagger(), PythonMajorMinorVersionTagger(), JavaMajorVersionTagger(), ScalaMajorMinorVersionTagger()),
            LongTagger(SparkVersionTagger(), PythonMajorMinorVersionTagger(), JavaMajorVersionTagger(), ScalaMajorMinorVersionTagger(), SHATagger()),
            LongTagger(SparkVersionTagger(), PythonMajorMinorVersionTagger(), JavaMajorVersionTagger(), ScalaMajorMinorVersionTagger(), DateTagger()),
            LongTagger(SparkVersionTagger(), PythonVersionTagger(), JavaVersionTagger(), ScalaVersionTagger(), JupyterHubVersionTagger(), JupyterLabVersionTagger()),
            LongTagger(SparkVersionTagger(), PythonVersionTagger(), JavaVersionTagger(), ScalaVersionTagger(), JupyterHubVersionTagger(), JupyterLabVersionTagger(), DateTagger()),
            ],
        manifests=[SparkInfoManifest()],
    ),
    "all-spark-notebook": ImageDescription(
        parent_image="pyspark-notebook",
        taggers=[
            LongTagger(SparkVersionTagger(), PythonVersionTagger(), RVersionTagger(), JavaVersionTagger(), ScalaVersionTagger(), JupyterHubVersionTagger(), JupyterLabVersionTagger()),
            LongTagger(SparkVersionTagger(), PythonVersionTagger(), RVersionTagger(), JavaVersionTagger(), ScalaVersionTagger(), JupyterHubVersionTagger(), JupyterLabVersionTagger(), DateTagger()),
        ],
        manifests=[RPackagesManifest()],
    ),
}
