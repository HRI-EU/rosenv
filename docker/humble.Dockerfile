FROM ros:humble-ros-core

ARG UID=1000
ARG GID=1000

RUN groupadd --gid ${GID} hri && useradd --home-dir /home/hri \
    --create-home --shell /bin/bash --uid ${UID} --gid ${GID} hri

RUN \
    --mount=type=cache,target=/var/cache/apt \
    apt-get update && \
    apt-get install --yes --no-install-recommends \
        build-essential \
        cmake \
        curl \
        debhelper \
        dh-python \
        fakeroot \
        git \
        python-is-python3 \
        python3-pip \
        sudo && \
    rm -rf /var/lib/apt/lists/* && \
    pip3 install --no-cache-dir poetry==1.8.3

RUN echo "hri ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/hri

USER hri
WORKDIR /home/hri
