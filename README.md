# kdp-docker-stacks

kdp jupyter images based on https://github.com/jupyter/docker-stacks


# Extension


# Initial setup

```shell
git remote add docker-stacks https://github.com/jupyter/docker-stacks.git
git subtree add --prefix=docker-stacks --squash docker-stacks main
```

```shell
act  --container-architecture linux/amd64  \
     -W .github/workflows/docker.yml \
     --artifact-server-path /tmp/act/artifacts \
     --env ACT_SKIP_TESTS=<true|false> \
     --env PUSH_TO_REGISTRY=true \
     --env REGISTRY=ghcr.io  \
     --secret REGISTRY_USERNAME=<GITHUB_OWNER> \
     --secret REGISTRY_ROBOT_TOKEN=<GITHUB_CONTAINER_REGISTRY_TOKEN>
     --rm
```