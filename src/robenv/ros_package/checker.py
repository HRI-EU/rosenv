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
from logging import getLogger
from pathlib import Path

from deb_pkg_tools.package import ArchiveEntry
from deb_pkg_tools.package import inspect_package_contents

from robenv.environment.env import Installable
from robenv.ros_package.package import ROSPackage
from robenv.util.paths import remove_slash_prefix


_logger = getLogger(__name__)


class LaunchFilesNotInstalledError(Exception):
    def __init__(self, missing: LaunchFilesCheckResult) -> None:
        super().__init__(
            f"1 or more launch files for package {missing.package.name} not installed, "
            f"following are missing:\n"
            f"{missing.missing_files}",
        )
        self.missing = missing


class CMakeListFileNotExistsError(Exception):
    def __init__(self, path: Path) -> None:
        self.path = path
        super().__init__(f"CMakeLists.txt at '{path!s}' doesn't exist!")


@dataclass
class LaunchFilesCheckResult:
    package: ROSPackage
    missing_files: list[Path]

    def __bool__(self) -> bool:
        return len(self.missing_files) > 0


@dataclass
class Checker:
    check: bool
    check_will_fail: bool

    def get_missing_launch_files(self, package: ROSPackage, installable: Installable) -> LaunchFilesCheckResult:
        if not self.check:
            return LaunchFilesCheckResult(package=package, missing_files=[])
        contents: dict[str, ArchiveEntry] = inspect_package_contents(str(installable.location))
        launch_files_in_deb = [Path(remove_slash_prefix(p)) for p in contents if p.endswith(".launch")]
        _logger.debug("Found launch files in deb-file: %s", launch_files_in_deb)

        launch_files_in_project = list(package.path.rglob("*.launch"))
        _logger.debug("Found launch files in project: %s", launch_files_in_project)

        launch_file_names_in_deb = [p.name for p in launch_files_in_deb]
        launch_file_names_in_project = [p.name for p in launch_files_in_project]

        missing_files = [
            file_name for file_name in launch_file_names_in_project if file_name not in launch_file_names_in_deb
        ]

        result = LaunchFilesCheckResult(
            package=package,
            missing_files=[file for file in launch_files_in_project if file.name in missing_files],
        )

        if self.check_will_fail and result.missing_files:
            raise LaunchFilesNotInstalledError(result)
        return result
