# service-runner

Repo containing the code for the server side system runner.
The runner is built as a docker container designed to be run on AWS Lambda

## Commands

Use the commands in the Makefile to work with this repo:

    make sdk

This will download the latest version of the SDK, and place it in runner/sdk/python-sdk

    make build

This will build the docker container for the runner.

    make run

This will start the docker container locally.

    make example1

This will do and HTTP POST to the running container with the payload from examples/example1.json