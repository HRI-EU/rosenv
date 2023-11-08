#
#  Copyright (C)
#  Honda Research Institute Europe GmbH
#  Carl-Legien-Str. 30
#  63073 Offenbach/Main
#  Germany
#
#  UNPUBLISHED PROPRIETARY MATERIAL.
#  ALL RIGHTS RESERVED.
#

.PHONY: all rosenv iron

DOCKER_CONTEXT=..
BUILD_ARGS=--build-arg http_proxy --build-arg https_proxy
CONTAINER_REGISTRY=dmz-gitlab.honda-ri.de:5050/gitlabrunner/buildcontainers

all: rosenv iron

rosenv: rosenv.Dockerfile
	docker build $(BUILD_ARGS) -t $(CONTAINER_REGISTRY)/$@ -f $@.Dockerfile $(DOCKER_CONTEXT)

iron: iron.Dockerfile
	docker build $(BUILD_ARGS) -t $(CONTAINER_REGISTRY)/$@ -f $@.Dockerfile $(DOCKER_CONTEXT)
