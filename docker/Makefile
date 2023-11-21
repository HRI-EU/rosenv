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

.PHONY: all rosenv

DOCKER_CONTEXT=..

all: rosenv

rosenv: iron.Dockerfile
	docker build -t localhost/$@ -f iron.Dockerfile $(DOCKER_CONTEXT)
