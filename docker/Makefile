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

robenv: humble.Dockerfile
	docker build -t localhost/$@ -f humble.Dockerfile $(DOCKER_CONTEXT)
