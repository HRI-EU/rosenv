#
#  Copyright (c) Honda Research Institute Europe GmbH
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#  1. Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
#
#  2. Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#
#  3. Neither the name of the copyright holder nor the names of its
#     contributors may be used to endorse or promote products derived from
#     this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
#  IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
#  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
#  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#

from __future__ import annotations

import os

from logging import getLogger
from pathlib import Path
from shutil import copy

import requests

from robenv.environment.distro import RosDistribution
from robenv.environment.distro import parse_distro
from robenv.environment.run_command import run_command


_logger = getLogger(__name__)


class ROS:
    path: Path
    distro: RosDistribution
    _distro_path: Path
    _archive_path: Path

    def __init__(self, path: str) -> None:
        cache_path = Path.home() / ".cache/robenv"
        xdg_home = os.environ.get("XDG_CACHE_HOME")
        if xdg_home is not None:
            cache_path = Path(xdg_home) / "robenv"

        if path.startswith("http") or path.endswith("tar.gz"):
            if "ros2" not in path:
                msg = "possible no ros2 archive, get a possible link/file from https://github.com/ros2/ros2/releases"
                raise ValueError(
                    msg,
                )
            file_name = path.split("/")[-1]
            # file_name is somthing like: ros2-humble-20231122-linux-jammy-amd64.tar.bz2
            file_name_split = file_name.split("-")
            distro_name = file_name_split[1]
            _logger.info("%s ", distro_name)
            self.distro = parse_distro(distro_name)
            self._archive_path = cache_path / file_name
            self._distro_path = cache_path / file_name.split(".")[0]
            cache_path.mkdir(parents=True, exist_ok=True)
            if "http" in path:
                self._download(path)
            else:
                self._copy_to_cache(Path(path))
            self._install()
            self.path = self._find_path()
        else:
            _logger.info(" %s ", path)
            self.distro = parse_distro(path.split("/")[3])
            self.path = Path(path)

    def _find_path(self) -> Path:
        search = self._distro_path.glob("**/setup.sh")
        return next(iter(search)).parent

    def _copy_to_cache(self, file_path: Path) -> None:
        if file_path.exists() and not self._archive_path.exists():
            copy(file_path, self._archive_path)

    def _download(self, url: str) -> None:
        if not self._archive_path.exists():
            _logger.debug("Download %s from %s", self._distro_path.name, url)
            download = requests.get(url, allow_redirects=True, timeout=60)
            self._archive_path.write_bytes(download.content)
            _logger.debug("saved %s at %s", self._distro_path.name, str(self._archive_path))

    def _install(self) -> None:
        if not self._distro_path.exists():
            self._distro_path.mkdir(parents=True, exist_ok=True)
            run_command(command=f"tar xfvj {self._archive_path!s} -C {self._distro_path}", cwd=Path.cwd())
            path = self._find_path()
            opt_ros_path = path.parent / "opt/ros"
            opt_ros_path.mkdir(exist_ok=True, parents=True)
            path.rename(opt_ros_path / self.distro)
