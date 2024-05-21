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
from typing import Final
from typing import Generator
from typing import Literal
from typing import TypeVar

import pytest

from robenv.environment.distro import DistroConfig
from robenv.environment.distro import RosDistribution
from robenv.environment.distro import get_distro_config
from robenv.environment.distro import get_installed_distro_paths
from robenv.environment.distro import parse_distro


_T = TypeVar("_T")
YieldFixture = Generator[_T, None, None]

ROS_1: Final[Literal[1]] = 1
ROS_2: Final[Literal[2]] = 2


def get_ros_version() -> Literal[1, 2]:
    installed_distro = get_installed_distro_paths()

    if len(installed_distro) == 0 or installed_distro[0].name != "noetic":
        return ROS_2

    return ROS_1


@pytest.fixture()
def ros_distro() -> RosDistribution:
    ros_name = get_installed_distro_paths()
    if len(ros_name) == 0:
        msg = "No ROS installation detected on system!"
        raise AssertionError(msg)
    return parse_distro(ros_name[0].name)


@pytest.fixture()
def ros_distro_config(ros_distro: RosDistribution) -> DistroConfig:
    return get_distro_config(ros_distro)


@pytest.fixture()
def resources() -> Path:
    return Path(__file__).parent / "resources"


@pytest.fixture()
def example_project_launch_files(resources: Path) -> Path:
    return resources / "example_project_launch_files"


@pytest.fixture()
def example_project_ros1(resources: Path) -> Path:
    return resources / "example_project_ros1"


@pytest.fixture()
def example_project_ros2(resources: Path) -> Path:
    return resources / "example_project_ros2"


@pytest.fixture()
def example_project(example_project_ros1: Path, example_project_ros2: Path) -> Path:
    if get_ros_version() == ROS_2:
        return example_project_ros2

    return example_project_ros1


ROS_1_PROJECT_LIST = ["adder", "adder_meta", "adder_srvs", "client", "python_server", "server"]
ROS_2_PROJECT_LIST = ["adder", "adder_srvs", "client", "python_server", "server"]


@pytest.fixture()
def project_list() -> list[str]:
    """
    Get list of projects for the current ROS version.

    Basic difference is, that under ROS2 there are no meta packages anymore.
    """
    if get_ros_version() == ROS_1:
        return ROS_1_PROJECT_LIST

    return ROS_2_PROJECT_LIST


@pytest.fixture()
def test_debs(resources: Path) -> Path:
    return resources / "test_debs"


@pytest.fixture()
def catkin_tools(resources: Path) -> Path:
    return resources / "catkin_tools"


@pytest.fixture()
def rosdistro_index(resources: Path) -> Path:
    return resources / "rosdistro_index/index-v4.yaml"
