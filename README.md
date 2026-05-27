<!-- Section 0 — Product image -->

<img src="https://jupyter.org/assets/homepage/main-logo.svg" alt="JupyterLab" height="48" align="right" />

<!-- Section 1 — Badges -->

[![ci](https://github.com/OKDP/jupyterlab-docker/actions/workflows/ci.yml/badge.svg)](https://github.com/OKDP/jupyterlab-docker/actions/workflows/ci.yml)
[![release-please](https://github.com/OKDP/jupyterlab-docker/actions/workflows/release-please.yml/badge.svg)](https://github.com/OKDP/jupyterlab-docker/actions/workflows/release-please.yml)
[![Release](https://img.shields.io/github/v/release/OKDP/jupyterlab-docker)](https://github.com/OKDP/jupyterlab-docker/releases/latest)
[![License Apache2](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](http://www.apache.org/licenses/LICENSE-2.0)
<a href="https://okdp.io">
  <img src="https://okdp.io/logos/okdp-notext.svg" height="20px" style="margin: 0 2px;" />
</a>

<!-- Section 2 — Project name + short description -->

# OKDP Jupyter Images

OKDP Jupyter Docker images built from the upstream [jupyter/docker-stacks](https://github.com/jupyter/docker-stacks) Dockerfiles, with an OKDP-maintained version compatibility matrix. The `pyspark-notebook` and `all-spark-notebook` images bundle Apache Spark binaries from the [OKDP Spark distribution](https://github.com/OKDP/spark-images/releases/tag/spark-tarballs) instead of `archive.apache.org`. The images are published to [`quay.io/okdp/jupyter`](https://quay.io/organization/okdp) and used as the singleuser image of the [OKDP sandbox](https://github.com/OKDP/okdp-sandbox) JupyterHub.

<!-- Section 3 — What the project does -->

## What the project does

This repository builds and publishes a matrix of JupyterLab / JupyterHub container images. It vendors the upstream [`jupyter/docker-stacks`](https://github.com/jupyter/docker-stacks) source as a [git-subtree](https://www.atlassian.com/git/tutorials/git-subtree) under [`docker-stacks/`](docker-stacks) and adds:

- **An OKDP-maintained version compatibility matrix** ([`.build/.versions.yml`](.build/.versions.yml)) — combinations of Python, Spark, Java, Scala known to work together.
- **Spark binaries from the [OKDP Spark distribution](https://github.com/OKDP/spark-images/releases/tag/spark-tarballs)** — for `pyspark-notebook` and `all-spark-notebook`, the Spark tarballs are downloaded from `OKDP/spark-images` GitHub releases (see [`spark_download_url` in `.build/.versions.yml`](.build/.versions.yml#L30)) instead of `archive.apache.org/dist/spark/`.
- **Multi-arch images** for `linux/amd64` and `linux/arm64` (since [v1.1.0](https://github.com/OKDP/jupyterlab-docker/releases/tag/v1.1.0)).
- **Local override layer** — [`scipy-notebook/Dockerfile`](scipy-notebook/Dockerfile) adds extra Python packages from [`scipy-notebook/requirements.txt`](scipy-notebook/requirements.txt) (`jupyter-fs[fsspec]`, `s3fs`, `jupysql`, `trino`, `sqlalchemy-trino`, `nbgitpuller`) on top of the upstream `scipy-notebook` Dockerfile. [`pyspark-notebook/Dockerfile`](pyspark-notebook/Dockerfile) is wired the same way with an empty [`pyspark-notebook/requirements.txt`](pyspark-notebook/requirements.txt) as a placeholder — packages are inherited transitively from `scipy-notebook`.
- **Custom Python extensions** under [`.build/python/src/okdp/`](.build/python/src/okdp/) — tagging, compatibility-matrix expansion, patches and unit tests (see [Development](#development)).

<!-- Section 4 — Architecture -->

## Architecture

The images follow the upstream [`jupyter/docker-stacks` inheritance chain](https://jupyter-docker-stacks.readthedocs.io/en/latest/using/selecting.html). Only the variants in **bold** are actually built and pushed to `quay.io/okdp/jupyter` today — `julia-notebook`, `tensorflow-notebook` and `pytorch-notebook` exist in [`docker-stacks/images/`](docker-stacks/images/) but their jobs are commented out in [`build-datascience-images-template.yml#L62-L90`](.github/workflows/build-datascience-images-template.yml#L62-L90).

<p align="center">
  <img src="docs/assets/architecture.svg" alt="OKDP Jupyter Images — inheritance chain" />
</p>

OKDP additions on top of the upstream Dockerfile are minimal — a single `pip install -r requirements.txt` layer in [`scipy-notebook/Dockerfile`](scipy-notebook/Dockerfile), reading [`scipy-notebook/requirements.txt`](scipy-notebook/requirements.txt). The same wiring exists in [`pyspark-notebook/Dockerfile`](pyspark-notebook/Dockerfile) with an empty [`pyspark-notebook/requirements.txt`](pyspark-notebook/requirements.txt) (placeholder).

<!-- Section 5 — Prerequisites -->

## Prerequisites

- [Docker](https://www.docker.com/) (BuildKit recommended).
- Enough free disk for the image you pull — `pyspark-notebook` is ~7 GB on disk after pull; `base-notebook` is significantly smaller.
- A free port `8888` on the host for the JupyterLab UI.

<!-- Section 6 — Quick Start + 6.1 Expected result -->

## Quick Start

Pull and run the `pyspark-notebook` image — the canonical OKDP image, which bundles Apache Spark, Java 17, Scala 2.13 and the scientific Python stack:

```sh
docker pull quay.io/okdp/jupyter/pyspark-notebook:spark-3.5.6-python-3.11-java-17-scala-2.13

docker run --rm -p 8888:8888 \
  quay.io/okdp/jupyter/pyspark-notebook:spark-3.5.6-python-3.11-java-17-scala-2.13
```

### Expected result

The container starts JupyterLab on port `8888` (via the upstream [`start-notebook.py`](docker-stacks/images/base-notebook/start-notebook.py) entrypoint) and prints a one-time access URL containing a token, for example:

```
[I ServerApp] Jupyter Server 2.x is running at:
[I ServerApp] http://localhost:8888/lab?token=<random-token>
[I ServerApp]     http://127.0.0.1:8888/lab?token=<random-token>
```

Open the `http://127.0.0.1:8888/lab?token=...` URL in your browser to reach the JupyterLab UI.

<!-- Section 7 — Installation -->

## Installation

All images are published to [`quay.io/okdp/jupyter`](https://quay.io/organization/okdp). Pull syntax:

```sh
docker pull quay.io/okdp/jupyter/<image>:<tag>
```

Where `<image>` is one of `docker-stacks-foundation`, `base-notebook`, `minimal-notebook`, `scipy-notebook`, `r-notebook`, `datascience-notebook`, `pyspark-notebook`, `all-spark-notebook` — and `<tag>` is any [published tag](#images) (the recommended pyspark tag as of v1.3.0 is `spark-3.5.6-python-3.11-java-17-scala-2.13`).

<!-- Section 8 — Configuration -->

## Configuration

### Build arguments

When rebuilding an image from `docker-stacks/images/<image>/Dockerfile`, the following `--build-arg` values are honoured (extracted from the upstream Dockerfiles):

| Build arg | Used in | Default | Description |
|:---|:---|:---|:---|
| `REGISTRY` | all | `quay.io` | Registry hosting the base image. |
| `OWNER` | all | `jupyter` | Owner of the base image — set to `okdp/jupyter` to chain off OKDP images. |
| `BASE_IMAGE` | all | `${REGISTRY}/${OWNER}/<parent>` | Full base image reference. |
| `ROOT_IMAGE` | `docker-stacks-foundation` | `ubuntu:24.04` | The Ubuntu base. |
| `NB_USER` | `docker-stacks-foundation` | `jovyan` | UNIX user inside the container. |
| `NB_UID` | `docker-stacks-foundation` | `1000` | UID of `NB_USER`. |
| `NB_GID` | `docker-stacks-foundation` | `100` | GID `NB_USER` belongs to. |
| `PYTHON_VERSION` | `docker-stacks-foundation` | `3.13` | Python version installed in the conda env. |
| `openjdk_version` | `pyspark-notebook` | `17` | OpenJDK major version. |
| `spark_version` | `pyspark-notebook` | *(required)* | Apache Spark version to bundle. |
| `hadoop_version` | `pyspark-notebook` | `3` | Hadoop major version embedded in the Spark tarball. |
| `scala_version` | `pyspark-notebook` | *(required)* | Scala version. |
| `spark_download_url` | `pyspark-notebook` | `https://dlcdn.apache.org/spark/` | Base URL for the Spark tarball — OKDP overrides this to `https://github.com/OKDP/spark-images/releases/download/spark-tarballs/` via [`.build/.versions.yml#L30`](.build/.versions.yml#L30). |

### Runtime environment variables

The defaults work out of the box (the [Quick Start](#quick-start) does not set any env variable). You override them with `docker run -e VAR=value` only when you need to — typically when mounting a host directory whose UID/GID does not match `1000:100`, or when running a Spark job that needs more memory.

Example: mount the current host directory as `/home/jovyan/work` and align the in-container user with the host user so files written by the notebook are owned by you:

```sh
docker run --rm -p 8888:8888 \
  -e NB_UID=$(id -u) -e NB_GID=$(id -g) -e CHOWN_HOME=yes \
  -v "$(pwd)":/home/jovyan/work \
  quay.io/okdp/jupyter/pyspark-notebook:spark-3.5.6-python-3.11-java-17-scala-2.13
```

Full list of variables honoured by [`docker-stacks-foundation/start.sh`](docker-stacks/images/docker-stacks-foundation/start.sh) at container startup:

| Variable | Default | Description |
|:---|:---|:---|
| `NB_USER` | `jovyan` | Desired username and associated home folder. |
| `NB_UID` | `1000` | Desired user id. |
| `NB_GID` | `100` | Group id the user belongs to. |
| `NB_GROUP` | *(unset)* | Group name. |
| `GRANT_SUDO` | *(unset)* | If `1` or `yes`, grant `${NB_USER}` passwordless `sudo`. |
| `CHOWN_HOME` | *(unset)* | If `1` or `yes`, `chown` `${HOME}` to `${NB_UID}:${NB_GID}` at start. |
| `CHOWN_EXTRA` | *(unset)* | Comma-separated list of additional paths to `chown`. |
| `JUPYTER_PORT` | `8888` | Port JupyterLab listens on inside the container (set in [`base-notebook/Dockerfile`](docker-stacks/images/base-notebook/Dockerfile)). |
| `SPARK_OPTS` | `--driver-java-options=-Xms1024M --driver-java-options=-Xmx4096M --driver-java-options=-Dlog4j.logLevel=info` | Extra options passed to `spark-submit` for `pyspark-notebook` / `all-spark-notebook` (set in [`pyspark-notebook/Dockerfile`](docker-stacks/images/pyspark-notebook/Dockerfile)). |

<!-- Section 10 — Images -->

## Images

All images are published under [`quay.io/okdp/jupyter`](https://quay.io/organization/okdp):

| Image | Description |
|:------|:------------|
| `docker-stacks-foundation` | Minimal Ubuntu + `mamba` + `jovyan` user. Foundation layer for all other images. |
| `base-notebook` | Adds JupyterLab, JupyterHub single-user, and Notebook. |
| `minimal-notebook` | Adds common CLI tools (`git`, `nano`, `tzdata`, fonts). |
| `scipy-notebook` | Adds the scientific Python stack (`pandas`, `scipy`, `matplotlib`, `scikit-learn`, `seaborn`, …) + OKDP additions ([`scipy-notebook/requirements.txt`](scipy-notebook/requirements.txt)): `jupyter-fs[fsspec]`, `s3fs`, `jupysql`, `trino`, `sqlalchemy-trino`, `nbgitpuller`. |
| `r-notebook` | `minimal-notebook` + R + IRKernel. |
| `datascience-notebook` | `scipy-notebook` + R + Julia. |
| `pyspark-notebook` | `scipy-notebook` + Apache Spark (from the [OKDP Spark distribution](https://github.com/OKDP/spark-images/releases/tag/spark-tarballs)) + Java + Scala. |
| `all-spark-notebook` | `pyspark-notebook` + R (`r-base`, `r-irkernel`, [`r-sparklyr`](https://spark.posit.co/)) for running R on Spark. |

> ℹ️ `julia-notebook`, `tensorflow-notebook` and `pytorch-notebook` exist as scaffolding in [`build-datascience-images-template.yml`](.github/workflows/build-datascience-images-template.yml) but are currently commented out and **not built or published**.

### Tag format

The project builds the images with long-format tags. Each tag combines multiple compatible version combinations. The examples below show the canonical tags published as of v1.3.0 (build date `2026-04-13`). Browse [`quay.io/okdp`](https://quay.io/organization/okdp) for the full list.

#### `scipy-notebook`
- `python-3.11-2026-04-13`
- `python-3.11.15-2026-04-13`
- `python-3.11.15-hub-5.4.4-lab-4.5.6`
- `python-3.11.15-hub-5.4.4-lab-4.5.6-2026-04-13`

#### `datascience-notebook`
- `python-3.11-2026-04-13`
- `python-3.11.15-2026-04-13`
- `python-3.11.15-hub-5.4.4-lab-4.5.6`
- `python-3.11.15-hub-5.4.4-lab-4.5.6-2026-04-13`
- `python-3.11.15-r-4.5.3-julia-1.12.6-2026-04-13`
- `python-3.11.15-r-4.5.3-julia-1.12.6-hub-5.4.4-lab-4.5.6`
- `python-3.11.15-r-4.5.3-julia-1.12.6-hub-5.4.4-lab-4.5.6-2026-04-13`

#### `pyspark-notebook`
- `spark-3.5.6-python-3.11-java-17-scala-2.13`
- `spark-3.5.6-python-3.11-java-17-scala-2.13-2026-04-13`
- `spark-3.5.6-python-3.11.15-java-17.0.18-scala-2.13.8-hub-5.4.4-lab-4.5.6`
- `spark-3.5.6-python-3.11.15-java-17.0.18-scala-2.13.8-hub-5.4.4-lab-4.5.6-2026-04-13`

<!-- Section 11 — OKDP integration -->

## OKDP integration

The [OKDP sandbox](https://github.com/OKDP/okdp-sandbox) deploys these images as the singleuser image of its JupyterHub release:

```yaml
# okdp-sandbox/packages/okdp-packages/jupyterhub/jupyterhub.yaml
singleuser:
  image:
    name: quay.io/okdp/jupyter/all-spark-notebook
    tag: "spark-3.5.6-python-3.11-java-17-scala-2.12"
```

→ [`okdp-sandbox/packages/okdp-packages/jupyterhub/jupyterhub.yaml`](https://github.com/OKDP/okdp-sandbox/blob/main/packages/okdp-packages/jupyterhub/jupyterhub.yaml)

Spawning a notebook server in the sandbox JupyterHub creates a pod running this image, with `SPARK_HOME` already set and the OKDP Spark distribution available — see [`okdp-sandbox` README](https://github.com/OKDP/okdp-sandbox#readme).

<!-- Section 12 — Development -->

## Development

### Update `jupyter/docker-stacks`

The [`docker-stacks/`](docker-stacks) folder is included in this repository as a [git subtree](https://www.atlassian.com/git/tutorials/git-subtree) — the upstream code is fully copied in, no submodule.

To bring in the latest upstream changes:

```sh
git remote add docker-stacks https://github.com/jupyter/docker-stacks.git  # if missing
git fetch docker-stacks
git subtree pull --prefix=docker-stacks docker-stacks main --squash
```

After the merge, make sure the OKDP custom extensions still pass their unit tests ([`.build/python/tests`](.build/python/tests)).

### OKDP custom extensions

Located under [`.build/python/src/okdp/`](.build/python/src/okdp/):

1. [Tagging extension](.build/python/src/okdp/extension/tagging) — based on the upstream [`jupyter/docker-stacks tagging`](docker-stacks/tagging) sources.
2. [Patches](.build/python/src/okdp/patch/README.md) — patches the upstream [tests](docker-stacks/tests) so they run against the OKDP image matrix.
3. [Version compatibility matrix](.build/python/src/okdp/extension/matrix) — generates all compatible version combinations for the pyspark build.
4. [Unit tests](.build/python/tests) — exercise the OKDP extensions at every pipeline run.

<!-- Section 13 — Build -->

## Build

The [`ci`](.github/workflows/ci.yml) build pipeline is composed of the following workflows (the `*-template.yml` files under [`.github/workflows/`](.github/workflows/) are reusable workflows called from `ci.yml` and `publish.yml`):

1. [`build-base-images-template`](.github/workflows/build-base-images-template.yml): `docker-stacks-foundation`, `base-notebook`, `minimal-notebook`, `scipy-notebook`
2. [`build-datascience-images-template`](.github/workflows/build-datascience-images-template.yml): `r-notebook`, `datascience-notebook` (`julia-notebook`, `tensorflow-notebook` and `pytorch-notebook` are commented out)
3. [`build-spark-images-template`](.github/workflows/build-spark-images-template.yml): `pyspark-notebook`, `all-spark-notebook`
4. [`publish`](.github/workflows/publish.yml): push the built images to the container registry (main branch only)
5. [`auto-rerun`](.github/workflows/auto-rerun.yml): partially re-run jobs in case of failures (GitHub runner issues / main branch only)
6. [`ci`](.github/workflows/ci.yml): run CI pipeline at every contribution

![build pipeline](doc/_images/build-pipeline.png)

The build is driven by [`.build/.versions.yml`](.build/.versions.yml). The [`build-matrix`](.build/.versions.yml#L80) section defines which component versions to build — it filters the parent [`compatibility-matrix`](.build/.versions.yml#L21) to limit the combinations actually built. Example:

```yaml
build-matrix:
  python_version: ['3.10', '3.11', '3.12']
  spark_version: [3.3.4, 3.4.2, 3.5.6]
  java_version: [17]
  scala_version: [2.12, 2.13]
```

→ produces these 6 compatible combinations (filtered against the `compatibility-matrix` — incompatible pairs like `python 3.10 + spark 3.5.x` or `python 3.12 + spark 3.x` are silently dropped):

- `spark3.3.4-python3.10-java17-scala2.12`
- `spark3.3.4-python3.10-java17-scala2.13`
- `spark3.4.2-python3.11-java17-scala2.12`
- `spark3.4.2-python3.11-java17-scala2.13`
- `spark3.5.6-python3.11-java17-scala2.12`
- `spark3.5.6-python3.11-java17-scala2.13`

### Publishing

Development images with the `-<GIT-BRANCH>-latest` suffix (e.g. `spark3.5.6-python3.11-java17-scala2.13-<GIT-BRANCH>-latest`) are produced at every pipeline run, regardless of the git branch.

Official images are published to [`quay.io/okdp/jupyter`](https://quay.io/organization/okdp) at every release **and** periodically, every Monday at 05:00 GMT (to pick up upstream security updates — see the `cron: "0 5 * * 1"` schedule in [`publish.yml`](.github/workflows/publish.yml)).

### Running locally with `act`

[`act`](https://github.com/nektos/act) can be used to run the workflows locally:

```sh
act --container-architecture linux/amd64 \
    -W .github/workflows/ci.yml \
    --env ACT_SKIP_TESTS=<true|false> \
    --secret GITHUB_TOKEN=<GITHUB_TOKEN> \
    --rm
```

(use `--container-architecture linux/amd64` on Apple Silicon — M1/M2/M3 — Macs.)

<!-- Section 14 — Test -->

## Test

With a `pyspark-notebook` container running (see [Quick Start](#quick-start)):

```sh
# Should return 200 (curl -L follows the redirect to the JupyterLab login page).
# A plain GET without -L returns 302 — that is expected, Jupyter redirects to /login with the token.
# Note: -I (HEAD) returns 405 because Jupyter rejects HEAD on /lab.
curl -sL -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8888/lab
```

### Expected result

```
200
```

For `pyspark-notebook` / `all-spark-notebook`, run a one-liner `SparkPi` job from inside the running container to confirm Spark is wired up:

```sh
CONTAINER_ID=$(docker ps --filter ancestor=quay.io/okdp/jupyter/pyspark-notebook --format '{{.ID}}' | head -1)

docker exec "$CONTAINER_ID" bash -lc '
  $SPARK_HOME/bin/spark-submit \
    --class org.apache.spark.examples.SparkPi \
    --master "local[2]" \
    $SPARK_HOME/examples/jars/spark-examples_*.jar 100 2>&1 | grep "Pi is roughly"
'
```

### Expected result

```
Pi is roughly 3.1407...
```

CI runs the upstream [`docker-stacks` tests](docker-stacks/tests) at every pipeline trigger, plus the OKDP [unit tests](.build/python/tests).

<!-- Section 16 — Contributing + License -->

## Contributing

Please follow the [OKDP contribution guide](https://github.com/OKDP/.github/blob/main/CONTRIBUTING.md): fork-based workflow, Conventional Commits, all PRs must be linked to an issue, ≥ 1 maintainer approval, all CI checks green.

## License

Apache License 2.0 — see [LICENSE](LICENSE).

<!-- Section 17 — Footer -->

---

**Built 🚀 for the OKDP Community**
<a href="https://okdp.io">
  <img src="https://okdp.io/logos/okdp-notext.svg" height="20px" style="margin: 0 2px;" />
</a>
