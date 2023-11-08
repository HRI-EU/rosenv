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

import yaml

from rosenv.catkin_profile.profile import CatkinProfile
from rosenv.environment.distro import RosDistribution
from rosenv.ros_package.workspace import ROSWorkspace
from rosenv.rosdep.rosdep import Rosdep
from rosenv.rosdep.rosdep import get_sources_list


def _create_rosdep_file(
    rosenv_directory: Path,
    workspace_path: Path,
    distro: RosDistribution,
) -> Path:
    rosdep_file = rosenv_directory.joinpath("rosdep.yaml").absolute()
    ros_workspace = ROSWorkspace.from_workspace(
        workspace_path,
        CatkinProfile.with_no_blacklist(),
    )

    rosdep_content = Rosdep.generate_rosdep_from_workspace(ros_workspace, distro)

    with Path.open(rosdep_file, "w") as file:
        yaml.dump(rosdep_content, file)

    return rosdep_file


def initialize_rosdep(
    rosenv_path: Path,
    workspace_path: Path,
    distro: RosDistribution,
    rosdep_path: Path | None = None,
) -> None:
    rosdep_source = get_sources_list(rosenv_path)
    rosdep_source.parent.mkdir(parents=True, exist_ok=True)
    rosdep_file = (
        rosdep_path
        if rosdep_path is not None
        else _create_rosdep_file(
            rosenv_path,
            workspace_path,
            distro,
        )
    )
    rosdep_source.write_text(
        f"yaml file://{rosdep_file!s}",
    )
