#
#  Docker image for Ubuntu 20.04 with poetry
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


FROM ubuntu:20.04

ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ENV PIP_DISABLE_PIP_VERSION_CHECK=1

ARG UID=2000
ARG GID=2000
ARG USE_HRI_REPOSITORY=True

RUN groupadd --gid ${GID} hri && useradd --home-dir /home/hri \
             --create-home --shell /bin/bash --uid ${UID} --gid ${GID} hri

# Replace official Ubuntu sources with HRI-EU apt mirror
# Installs hri apt keyring (one-time insecure with warning, due to missing key)
# This is needed for using the HRI-EU's apt mirror
# echo is the posix echo -> 'man 1p echo'
RUN if [ "${USE_HRI_REPOSITORY}" = "True" ]; then \
        echo '\n\
            deb http://hri-debian.honda-ri.de/ubuntu/ubuntu/ focal main restricted universe multiverse \n\
            deb http://hri-debian.honda-ri.de/ubuntu/ubuntu/ focal-updates main restricted universe multiverse \n\
            deb http://hri-debian.honda-ri.de/ubuntu/ubuntu/ focal-security main restricted universe multiverse \n\
            deb http://hri-debrepo.honda-ri.de/repo/ hri-debrepo focal' > /etc/apt/sources.list && \
        apt-get update --allow-insecure-repositories && \
        apt-get install --allow-unauthenticated -y \
                hri-debian-repository-keyring ros-gazebo-hri-keyring ; \
    fi

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
            python-is-python3 python3-pip git curl && \
    rm -rf /var/lib/apt/lists/*

# Download HRI CA certificate bundle
RUN curl -s -o /usr/local/share/ca-certificates/HRI-CA_cert.crt \
         --create-dirs http://intranet.honda-ri.de/HRI-CA_cert.crt

# HRI CA bundle as default for `requests`. Note that afterwards no access to non-HRI hosts is possible via `requests`
ENV REQUESTS_CA_BUNDLE=/usr/local/share/ca-certificates/HRI-CA_cert.crt

# HRI CA bundle as default for `git`. Note that afterwards no access to non-HRI hosts is possible via `git`
RUN git config --system http.sslCAInfo /usr/local/share/ca-certificates/HRI-CA_cert.crt

RUN pip3 install --no-cache-dir poetry==1.5.1

# Lowering SECLEVEL to 1 to allow weak self-signed certificate
RUN mv /etc/ssl/openssl.cnf /etc/ssl/openssl.orig && \
    echo "openssl_conf = default_conf" > /etc/ssl/openssl.cnf && \
    cat /etc/ssl/openssl.orig >> /etc/ssl/openssl.cnf && \
    rm /etc/ssl/openssl.orig && \
    echo "\n\
[ default_conf ]\n\
ssl_conf = ssl_sect\n\n\
[ ssl_sect ]\n\
system_default = system_default_sect\n\n\
[ system_default_sect ]\n\
MinProtocol = TLSv1.2\n\
CipherString = DEFAULT:@SECLEVEL=1\
" >> /etc/ssl/openssl.cnf

USER hri

