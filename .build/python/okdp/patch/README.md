# Patchs

The directory contains a list of a patched original python sourcen files in order to run the tests:

## Add ghcr.io container registry
* [run_tests.py](tests/run_tests.py#L53)

## Skip python version check
* [Skip python version](tests/docker-stacks-foundation/test_python_version.py#L17): Ability to run with any python version provided by the build-arg: PYTHON_VERSION

