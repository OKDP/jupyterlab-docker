#!/usr/bin/env python3
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

"""
Modification of the original file:
* Generate and apply the tags on the fly instead of writing them to an intermediate file
"""
import argparse
import logging

import plumbum

from tagging.docker_runner import DockerRunner
from okdp.extension.tagging.get_taggers_and_manifests import get_taggers_and_manifests

docker = plumbum.local["docker"]

LOGGER = logging.getLogger(__name__)

class Tagging:

    def __init__(self, short_image_name: str, registry: str, owner: str,):
        self.short_image_name, self.tag = short_image_name.split(":")
        self.registry = registry
        self.owner = owner

    def apply_tags(self) -> None:
        """
        Tags <registry>/<owner>/<short_image_name>:tag with the tags reported by all taggers for this image
        """
        LOGGER.info(f"Tagging image: {self.short_image_name}")

        image = f"{self.registry}/{self.owner}/{self.short_image_name}:{self.tag}"
        
        tags = self.generate_tags()

        for tag in tags:
            LOGGER.info(f"Applying tag: {tag}")
            docker["tag", image, tag] & plumbum.FG

    def generate_tags(self) -> [str]:
        """
        Generate tags for the image <registry>/<owner>/<short_image_name>:latest
        """
        LOGGER.info(f"Tagging image: {self.short_image_name}")
        taggers, _ = get_taggers_and_manifests(self.short_image_name)

        image = f"{self.registry}/{self.owner}/{self.short_image_name}:{ self.tag }"
        tags = [f"{self.registry}/{self.owner}/{self.short_image_name}:{ self.tag }"]
        with DockerRunner(image) as container:
            for tagger in taggers:
                tagger_name = tagger.__class__.__name__
                tag_value = tagger.tag_value(container)
                LOGGER.info(
                    f"Calculated tag, tagger_name: {tagger_name} tag_value: {tag_value}"
                )
                tags.append(
                    f"{self.registry}/{self.owner}/{self.short_image_name}:{tag_value}"
                )

        return tags


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "--short-image-name",
        required=True,
        help="Short image name",
    )
    arg_parser.add_argument(
        "--registry",
        required=True,
        type=str,
        choices=["ghcr.io"],
        help="Image registry",
    )
    arg_parser.add_argument(
        "--owner",
        required=True,
        help="Owner of the image",
    )
    args = arg_parser.parse_args()

    tagging = Tagging(args.short_image_name, args.registry, args.owner)
    
    tagging.apply_tags()
