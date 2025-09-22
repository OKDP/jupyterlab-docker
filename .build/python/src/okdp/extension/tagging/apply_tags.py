#!/usr/bin/env python3
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

"""
Modification of the original file:
* Generate and apply the tags on the fly instead of writing them to an intermediate file
"""
import logging
import plumbum
import argparse

from tagging.utils.docker_runner import DockerRunner
from okdp.extension.tagging.get_taggers_and_manifests import get_taggers_and_manifests

docker = plumbum.local["docker"]

LOGGER = logging.getLogger(__name__)

class Tagging:

    def __init__(self, image_name: str, registry: str, owner: str, platform: str,):
        self.image_name, self.tag = image_name.split(":")
        self.registry = registry
        self.owner = owner
        self.platform = platform

    def apply_tags(self) -> None:
        """
        Tags <registry>/<owner>/<image_name>:tag with the tags reported by all taggers for this image
        """
        LOGGER.info(f"Tagging image: {self.image_name}")

        image = f"{self.registry}/{self.owner}/{self.image_name}:{self.tag}-{self.platform}"
        
        tags = self.generate_tags()

        for tag in tags:
            LOGGER.info(f"Applying tag: {tag}")
            docker["tag", image, tag] & plumbum.FG

    def generate_tags(self) -> list[str]:
        """
        Generate tags for the image <registry>/<owner>/<image_name>:latest
        """
        LOGGER.info(f"Tagging image: {self.image_name}")
        taggers, _ = get_taggers_and_manifests(self.image_name)

        image = f"{self.registry}/{self.owner}/{self.image_name}:{self.tag}-{self.platform}"
        tags = [f"{self.registry}/{self.owner}/{self.image_name}:{self.tag}-{self.platform}"]
        with DockerRunner(image) as container:
            for tagger in taggers:
                tagger_name = tagger.__class__.__name__
                tag_value = tagger.tag_value(container)
                LOGGER.info(
                    f"Calculated tag, tagger_name: {tagger_name} tag_value: {tag_value}"
                )
                tags.append(
                    f"{self.registry}/{self.owner}/{self.image_name}:{tag_value}-{self.platform}"
                )

        return tags


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "--image-name",
        required=True,
        help="Image name:tag",
    )
    arg_parser.add_argument(
        "--registry",
        required=True,
        type=str,
        choices=["quay.io", "ghcr.io"],
        help="Image registry",
    )
    arg_parser.add_argument(
        "--owner",
        required=True,
        help="Owner of the image",
    )
    arg_parser.add_argument(
        "--platform",
        required=True,
        type=str,
        choices=["amd64", "arm64"],
        help="Platform",
    )
    args = arg_parser.parse_args()

    tagging = Tagging(args.image_name, args.registry, args.owner, args.platform)
    
    tagging.apply_tags()
