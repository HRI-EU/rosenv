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

from dataclasses import dataclass
from logging import DEBUG
from logging import getLogger
from pathlib import Path
from typing import ClassVar

from robenv.catkin_profile import CatkinProfile
from robenv.ros_package.package import ExternalDependency
from robenv.ros_package.package import PackageName
from robenv.ros_package.package import ROSPackage


_logger = getLogger(__name__)


@dataclass
class ROSWorkspace:
    path: Path
    ros_packages: list[ROSPackage]
    external_dependencies: list[ExternalDependency]

    exclude_locations: ClassVar[list[str]] = [
        ".catkin_tools",
        "build",
        "devel",
        "debian",
    ]

    robenv_marker_file: ClassVar[str] = "robenv/settings.yaml"

    @classmethod
    def from_workspace(cls, workspace_path: Path, profile: CatkinProfile) -> ROSWorkspace:
        absolute_workspace_path = workspace_path.absolute()
        ros_packages = ROSWorkspace._get_ros_packages(absolute_workspace_path, profile)
        external_dependencies = ROSWorkspace._get_external_dependencies(ros_packages)
        return cls(
            absolute_workspace_path,
            ros_packages,
            external_dependencies,
        )

    @staticmethod
    def _get_ros_packages(workspace_path: Path, profile: CatkinProfile) -> list[ROSPackage]:
        packages = ROSWorkspace._get_project_packages_paths(workspace_path)
        ros_packages = [ROSPackage.from_project(workspace_path / package) for package in packages]

        if _logger.isEnabledFor(DEBUG):
            _logger.debug("Found unfiltered packages: %s", [p.path for p in ros_packages])

        filtered_packages = [p for p in ros_packages if p.name not in profile.blacklist]
        filtered_packages.sort(key=lambda package: package.name)

        if _logger.isEnabledFor(DEBUG):
            _logger.debug("Found unblacklisted packages: %s", [p.path for p in filtered_packages])

        return filtered_packages

    @staticmethod
    def _is_filtered_path(path: Path) -> bool:
        return path.name in ROSWorkspace.exclude_locations or (path / ROSWorkspace.robenv_marker_file).exists()

    @staticmethod
    def _is_valid_package(package_dir: Path) -> bool:
        return not any(ROSWorkspace._is_filtered_path(path) for path in package_dir.parents)

    @staticmethod
    def _get_project_packages_paths(directory: Path = Path("src")) -> list[Path]:
        paths = [f.parent for f in directory.rglob("package.xml") if ROSWorkspace._is_valid_package(f)]
        paths.sort()
        return paths

    @staticmethod
    def _get_external_dependencies(ros_packages: list[ROSPackage]) -> list[ExternalDependency]:
        deps: dict[PackageName, list[ROSPackage]] = {}
        ros_packages_name_list = [ep.name for ep in ros_packages]

        for package in ros_packages:
            dependency_names = set(package.get_build_dependencies() + package.get_exec_dependencies())
            for name in dependency_names:
                if name not in ros_packages_name_list:
                    pkg_name = PackageName(name)

                    if pkg_name in deps:
                        deps[pkg_name].append(package)
                    else:
                        deps[pkg_name] = [package]

        return [ExternalDependency(dep, required_by=deps[dep]) for dep in deps]

    def sort_ros_packages_for_installation(self) -> list[ROSPackage]:
        sorted_packages: list[ROSPackage] = []
        external_dependencies = {ep.name for ep in self.external_dependencies}

        iteration = 0
        max_iterations = 3
        while len(self.ros_packages) > len(sorted_packages) and iteration < max_iterations:
            for package in self.ros_packages:
                if package in sorted_packages:
                    continue

                ros_package_dependencies = set(package.get_build_dependencies())
                ros_package_dependencies -= external_dependencies

                if len(ros_package_dependencies) == 0:
                    sorted_packages.append(package)
                    continue

                already_queued_packages = [p.name for p in sorted_packages]
                unresolved_dependencies = [
                    name for name in ros_package_dependencies if name not in already_queued_packages
                ]

                if len(unresolved_dependencies) == 0:
                    sorted_packages.append(package)
            iteration += 1

        return sorted_packages

    def get_install_tree(self) -> list[list[ROSPackage]]:
        external_dependencies_set = {ep.name for ep in self.external_dependencies}

        queues: list[list[ROSPackage]] = []
        queue: list[ROSPackage] = []
        for package in self.sort_ros_packages_for_installation():
            queued_dependencies = {dep.name for q in queues for dep in q}
            package_depencencies = (
                set(package.get_build_dependencies()) - external_dependencies_set - queued_dependencies
            )

            if len(package_depencencies) == 0:
                queue.append(package)
                continue

            current_queue_deps = {deb.name for deb in queue}
            if len(package_depencencies - current_queue_deps) == 0:
                queues.append(list(queue))
                queue = [package]

        queues.append(list(queue))

        return queues
