from __future__ import annotations

import os

from logging import getLogger
from pathlib import Path
from shutil import copy

import requests

from rosenv.environment.distro import RosDistribution
from rosenv.environment.distro import parse_distro
from rosenv.environment.run_command import run_command


_logger = getLogger(__name__)


class ROS:
    path: Path
    distro: RosDistribution
    _distro_path: Path
    _archive_path: Path

    def __init__(self, path: str) -> None:
        cache_path = Path.home() / ".cache/rosenv"
        xdg_home = os.environ.get("XDG_HOME")
        if xdg_home is not None:
            cache_path = Path(xdg_home) / "rosenv"

        if "http" in path or "tar.gz" in path:
            if "ros2" not in path:
                raise ValueError(
                    "possible no ros2 archive, get a possible link/file from https://github.com/ros2/ros2/releases"
                )
            file_name = path.split("/")[-1]
            file_name_split = file_name.split("-")
            distro = file_name_split[1]
            self.distro = parse_distro(distro)
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
            self.distro = parse_distro(path.split())
            self.path = Path(path)

    def _find_path(self) -> Path:
        search = self._distro_path.glob("**/setup.sh")
        return next(iter(search)).parent

    def _copy_to_cache(self, file_ath: Path) -> None:
        if file_ath.exists() and not self._archive_path.exists():
            copy(file_ath.as_posix(), self._archive_path.as_posix())

    def _download(self, url: str) -> None:
        if not self._archive_path.exists():
            _logger.debug("Download %s from %s", self._distro_path.name, url)
            download = requests.get(url, allow_redirects=True, timeout=60)
            self._archive_path.write_bytes(download.content)
            _logger.debug("saved %s at %s", self._distro_path.name, str(self._archive_path))

    def _install(self) -> None:
        if not self._distro_path.exists():
            self._distro_path.mkdir(parents=True, exist_ok=True)
            run_command(command=f"tar xfvj {self._archive_path.as_posix()} -C {self._distro_path}", cwd=Path.cwd())
            path = self._find_path()
            opt_ros_path = path.parent / "opt/ros"
            opt_ros_path.mkdir(exist_ok=True, parents=True)
            path.rename(opt_ros_path / self.distro)
