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

.PHONY: all robenv

DOCKER_CONTEXT=..

all: robenv

robenv: iron.Dockerfile
	docker build -t localhost/$@ -f iron.Dockerfile $(DOCKER_CONTEXT)
