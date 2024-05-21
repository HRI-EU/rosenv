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

import pytest

from robenv.catkin_profile.profile import CatkinProfile
from robenv.environment.distro import RosDistribution
from robenv.ros_package.workspace import ROSWorkspace
from robenv.rosdep.rosdep import ResolvedPackageName
from robenv.rosdep.rosdep import Rosdep
from robenv.rosdep.rosdep import RosDepDict
from robenv.rosdep.rosdep import SystemName


@pytest.fixture()
def expected_rosdep(ros_distro: RosDistribution) -> RosDepDict:
    ubuntu = SystemName("ubuntu")

    result: RosDepDict = {
        "adder": {ubuntu: [ResolvedPackageName(f"ros-{ros_distro}-adder")]},
        "adder_srvs": {ubuntu: [ResolvedPackageName(f"ros-{ros_distro}-adder-srvs")]},
        "client": {ubuntu: [ResolvedPackageName(f"ros-{ros_distro}-client")]},
        "python_server": {ubuntu: [ResolvedPackageName(f"ros-{ros_distro}-python-server")]},
        "server": {ubuntu: [ResolvedPackageName(f"ros-{ros_distro}-server")]},
    }

    if ros_distro == "noetic":
        result["adder_meta"] = {ubuntu: [ResolvedPackageName("ros-noetic-adder-meta")]}

    return result


def test_generate_should_give_dict_to_workspace(
    example_project: Path,
    expected_rosdep: RosDepDict,
    ros_distro: RosDistribution,
) -> None:
    workspace = ROSWorkspace.from_workspace(
        example_project,
        CatkinProfile.with_no_blacklist(),
    )

    rosdep = Rosdep.generate_rosdep_from_workspace(
        workspace,
        ros_distro,
    )

    assert rosdep == expected_rosdep
