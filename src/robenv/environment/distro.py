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

from pathlib import Path
from typing import Callable
from typing import Iterable
from typing import Literal
from typing import NamedTuple


RosDistribution = Literal["noetic", "foxy", "galactic", "iron", "rolling", "humble", "melodic"]
RenameStrategy = Callable[[RosDistribution, str], str]


def _default_rename_strategy(distro: RosDistribution, package_name: str) -> str:
    return f"ros-{distro}-{package_name.replace('_', '-')}"


class DistroConfig(NamedTuple):
    files_to_copy: Iterable[str]
    files_to_link: Iterable[str]
    builder_tool_variable_name: str
    meta_package_prevent_overwrite: Iterable[str]
    rename_strategy: RenameStrategy


ROS1_DEFAULT_CONFIG = DistroConfig(
    files_to_copy=(
        "local_setup.bash",
        "local_setup.zsh",
        "setup.bash",
        "setup.zsh",
    ),
    files_to_link=(
        ".catkin",
        ".rosinstall",
        "_setup_util.py",
        "bin",
        "env.sh",
        "etc",
        "include",
        "lib",
        "share",
    ),
    builder_tool_variable_name="_CATKIN_SETUP_DIR",
    meta_package_prevent_overwrite=(
        ".catkin",
        ".rosinstall",
        "_setup_util.py",
        "env.sh",
        "local_setup.bash",
        "local_setup.sh",
        "local_setup.zsh",
        "setup.bash",
        "setup.sh",
        "setup.zsh",
    ),
    rename_strategy=_default_rename_strategy,
)

ROS2_DEFAULT_CONFIG = DistroConfig(
    files_to_copy=(
        "_local_setup_util.py",
        "local_setup.bash",
        "local_setup.sh",
        "local_setup.zsh",
        "setup.bash",
        "setup.zsh",
    ),
    files_to_link=(
        "bin",
        "cmake",
        "include",
        "lib",
        "opt",
        "share",
        "src",
        "tools",
    ),
    builder_tool_variable_name="AMENT_CURRENT_PREFIX",
    meta_package_prevent_overwrite=(
        "_local_setup_util.py",
        "local_setup.bash",
        "local_setup.sh",
        "local_setup.zsh",
        "setup.bash",
        "setup.sh",
        "setup.zsh",
    ),
    rename_strategy=_default_rename_strategy,
)

_distro_map: dict[RosDistribution, DistroConfig] = {
    "melodic": ROS1_DEFAULT_CONFIG,
    "noetic": ROS1_DEFAULT_CONFIG,
    "foxy": ROS2_DEFAULT_CONFIG,
    "galactic": ROS2_DEFAULT_CONFIG,
    "iron": ROS2_DEFAULT_CONFIG,
    "humble": ROS2_DEFAULT_CONFIG,
    "rolling": ROS2_DEFAULT_CONFIG,
}

_IsEOL = bool
# snapshot from 2023-08-01
_distro_list: dict[RosDistribution, _IsEOL] = {
    "noetic": False,
    "rolling": False,
    "iron": False,
    "humble": False,
    "melodic": True,
    "galactic": True,
    "foxy": True,
}


class UnknownRosDistributionError(Exception):
    def __init__(self, distribution: str | None = None) -> None:
        msg = (
            "Distribution is completely unknown!"
            if distribution is None
            else f"Distribution {distribution} is unknown! "
            "If this is a new distribution please file an issue with robenv"
        )
        super().__init__(msg)


def get_installed_distro_paths(*, base_ros_path: Path = Path("/opt/ros")) -> list[Path]:
    return [base_ros_path / distro for distro in _distro_list if (base_ros_path / distro).exists()]


def parse_distro(distro: str) -> RosDistribution:
    if distro in _distro_map:
        return distro  # type: ignore[return-value]

    raise UnknownRosDistributionError(distro)


def get_distro_config(distro: RosDistribution) -> DistroConfig:
    return _distro_map[distro]


def is_eol_distro(distro: RosDistribution) -> bool:
    return _distro_list.get(distro, True)
