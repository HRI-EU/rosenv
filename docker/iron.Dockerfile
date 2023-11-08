FROM osrf/ros:iron-desktop-full

ARG UID=2000
ARG GID=2000

RUN groupadd --gid ${GID} hri && useradd --home-dir /home/hri \
    --create-home --shell /bin/bash --uid ${UID} --gid ${GID} hri

RUN \
    --mount=type=cache,target=/var/cache/apt \
    apt-get update && \
    apt-get install --yes --no-install-recommends \
    python-is-python3 python3-pip git curl && \
    rm -rf /var/lib/apt/lists/* && \
    pip3 install --no-cache-dir poetry==1.5.1

RUN echo "hri ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/hri

USER hri
WORKDIR /home/hri
