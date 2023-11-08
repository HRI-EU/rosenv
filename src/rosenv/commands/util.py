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

from rosenv.catkin_profile.parse import get_profile
from rosenv.catkin_profile.profile import CatkinProfile
from rosenv.environment.distro import get_installed_distro_paths
from rosenv.environment.env import RosEnv
from rosenv.ros_package.workspace import ROSWorkspace


class PathDoesNotExistError(Exception):
    def __init__(self, path: Path) -> None:
        self.path = path
        super().__init__(f"Path '{path!s}' doesn't exist!")


def verify_existing_paths(*paths: Path) -> None:
    if not all((non_existing_path := path).exists() for path in paths):
        raise PathDoesNotExistError(non_existing_path)


def get_catkin_tools_folder(rosenv_path: Path, catkin_tools_folder: str | None = None) -> Path:
    if catkin_tools_folder is not None:
        return Path(catkin_tools_folder).absolute()

    return (rosenv_path.parent / ".catkin_tools").absolute()


def get_optional_profile(
    catkin_tools_folder: Path,
    profile_name: str | None,
) -> CatkinProfile:
    if profile_name is None:
        return CatkinProfile.with_no_blacklist()

    return get_profile(catkin_tools_folder, profile_name)


def get_workspace(
    workspace_path: Path,
    rosenv: RosEnv,
    catkin_tools_folder: str | None = None,
    profile_name: str | None = None,
) -> ROSWorkspace:
    return ROSWorkspace.from_workspace(
        workspace_path,
        get_optional_profile(
            get_catkin_tools_folder(
                rosenv.path,
                catkin_tools_folder,
            ),
            profile_name,
        ),
    )


class NoRosInstallationDetectedError(Exception):
    def __init__(self) -> None:
        super().__init__("We didn't detect any ros installations!")


def get_default_ros_path() -> None | str:
    installed_distros = get_installed_distro_paths()

    if len(installed_distros) == 0:
        return None

    return str(installed_distros[0])
