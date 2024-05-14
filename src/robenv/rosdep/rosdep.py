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
from sys import stdout
from typing import Dict
from typing import List
from typing import NewType
from typing import Union

import yaml

from robenv.environment.distro import RosDistribution
from robenv.environment.distro import get_distro_config
from robenv.environment.distro import is_eol_distro
from robenv.environment.run_command import CommandFailedError
from robenv.environment.shell import RobEnvShell
from robenv.ros_package.package import PackageName
from robenv.ros_package.workspace import ROSWorkspace


ResolvedPackageName = NewType("ResolvedPackageName", str)
RosDepDependency = str
SystemName = NewType("SystemName", str)
Pip = str
Packages = str
PackageTranslations = List[ResolvedPackageName]
SystemCodeName = str  # buster | stretch | focal | bionic | "*"

PipPackages = Dict[  # with pip packages
    Pip,  # pip
    Dict[
        Packages,  # packages
        PackageTranslations,  # actual translations
    ],
]

TranslationDict = Union[
    Dict[
        SystemCodeName,  # version
        Union[
            None,  # null
            PipPackages,
            PackageTranslations,
        ],
    ],
    PipPackages,
    PackageTranslations,
]

RosDepDict = Dict[
    RosDepDependency,
    Dict[SystemName, TranslationDict],
]


class NotResolvablePackageError(Exception):
    def __init__(self, package_name: str) -> None:
        super().__init__(f"Cannot find {package_name} via rosdep resolve")
        self.package_name = package_name


def get_sources_list(robenv_path: Path) -> Path:
    return (robenv_path / "etc/ros/rosdep/sources.list.d/50-robenv.list").absolute()


class Rosdep:
    def __init__(self, robenv_path: Path, shell: RobEnvShell) -> None:
        with get_sources_list(robenv_path).open() as sources_list:
            self._path = Path(sources_list.readline()[len("yaml file://") :])
        with self._path.open() as file:
            self._rosdep_yml: RosDepDict = yaml.safe_load(file)
        self._shell = shell

    @staticmethod
    def get_rosdep_system() -> SystemName:
        # Currently we only support "autodetection" for ubuntu
        return SystemName("ubuntu")

    @staticmethod
    def generate_rosdep_from_workspace(workspace: ROSWorkspace, distro: RosDistribution) -> RosDepDict:
        distro_config = get_distro_config(distro)

        rosdep_content: RosDepDict = {
            PackageName(package.name): {
                Rosdep.get_rosdep_system(): [
                    ResolvedPackageName(distro_config.rename_strategy(distro, package.name)),
                ],
            }
            for package in workspace.ros_packages
        }

        return rosdep_content

    def get_rosdep_yml_file_path(self) -> Path:
        return self._path

    def add_pip(self, system: SystemName, package_name: PackageName, resolved_name: ResolvedPackageName) -> None:
        self._rosdep_yml[package_name] = {system: {"pip": {"packages": [resolved_name]}}}

    def add(self, system: SystemName, package_name: PackageName, resolved_name: ResolvedPackageName) -> None:
        self._rosdep_yml[package_name] = {system: [resolved_name]}

    def remove(self, package_name: PackageName) -> None:
        del self._rosdep_yml[package_name]

    def resolve(self, package_name: PackageName) -> ResolvedPackageName:
        cmd_package = f"rosdep resolve {package_name}"
        try:
            command_output = self._shell.run(cmd_package, Path.cwd())
            return ResolvedPackageName(command_output.splitlines()[1])
        except CommandFailedError as cf_err:
            raise NotResolvablePackageError(package_name) from cf_err

    def save(self) -> None:
        with self._path.open("w") as file:
            yaml.dump(self._rosdep_yml, stream=file)

    def print_to_stdout(self) -> None:
        yaml.dump(self._rosdep_yml, stream=stdout)

    def update(self, distro: RosDistribution | None = None) -> None:
        cmd = "rosdep update"
        if distro is not None and is_eol_distro(distro):
            cmd = "rosdep update --include-eol-distros"

        self._shell.run(cmd, Path.cwd())

    def init(self) -> None:
        self._shell.run("rosdep init", Path.cwd())
