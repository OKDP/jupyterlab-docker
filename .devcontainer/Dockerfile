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

# Base image: Ubuntu 24.04 (multi-arch: x86_64 + arm64)
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    sudo \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY docker-stacks/requirements-dev.txt /tmp/requirements-dev-1.txt
COPY .build/python/requirements-dev.txt /tmp/requirements-dev-2.txt
RUN cat /tmp/requirements-dev-1.txt /tmp/requirements-dev-2.txt > /tmp/requirements.txt

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN echo 'source /opt/venv/bin/activate' >> /etc/bash.bashrc

RUN pip install --upgrade pip setuptools wheel \
    && pip install -r /tmp/requirements.txt

