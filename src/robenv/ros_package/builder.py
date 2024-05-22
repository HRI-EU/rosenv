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

from concurrent.futures import as_completed
from dataclasses import dataclass
from dataclasses import field
from functools import lru_cache
from logging import DEBUG
from logging import getLogger
from pathlib import Path
from shutil import rmtree

from robenv.environment.distro import get_distro_config
from robenv.environment.env import DebName
from robenv.environment.env import Installable
from robenv.environment.env import RobEnv
from robenv.environment.run_command import CommandAbortedError
from robenv.environment.run_command import CommandFailedError
from robenv.ros_package.checker import Checker
from robenv.ros_package.checker import LaunchFilesCheckResult
from robenv.ros_package.package import PackageName
from robenv.ros_package.package import ROSPackage
from robenv.ros_package.workspace import ROSWorkspace
from robenv.util.cancelable_executor import CancelableExecutor
from robenv.util.file_logger import write_log


_logger = getLogger(__name__)


@dataclass()
class BuildResult:
    installables: list[Installable] = field(default_factory=list)
    failed_packages: list[str] = field(default_factory=list)
    missing_launch_files: list[LaunchFilesCheckResult] = field(default_factory=list)

    def __add__(self, other: BuildResult) -> BuildResult:
        self.installables += other.installables
        self.failed_packages += other.failed_packages
        self.missing_launch_files += other.missing_launch_files
        return self


class Builder:
    def __init__(  # noqa: PLR0913
        self,
        robenv: RobEnv,
        dist_folder: Path,
        *,
        overwrite: bool,
        max_workers: int,
        checker: Checker,
        can_fail: bool,
    ) -> None:
        self._robenv = robenv
        self._dist_folder = dist_folder
        self._overwrite = overwrite
        self._max_workers = max_workers
        self._checker = checker
        self._can_fail = can_fail

    @staticmethod
    def clear_package_cache(package: ROSPackage) -> None:
        obj_cache = package.path / ".obj-x86_64-linux-gnu"
        debian_files = package.path / "debian"

        rmtree(obj_cache, ignore_errors=True)
        rmtree(debian_files, ignore_errors=True)

    def build_workspace(
        self,
        workspace: ROSWorkspace,
    ) -> BuildResult:
        install_tree = workspace.get_install_tree()
        _logger.info("Building in %s stages", len(install_tree))

        result = BuildResult()
        with CancelableExecutor(max_workers=self._max_workers) as pool:
            for level, stage in enumerate(install_tree):
                if _logger.isEnabledFor(DEBUG):
                    _logger.debug("Build Order (level=%s): %s", level, [p.name for p in stage])

                futures = {pool.submit(self.build_package, package): package for package in stage}
                built_stage: list[tuple[ROSPackage, Installable]] = []
                for future in as_completed(futures):
                    package = futures[future]
                    build_result = future.result()
                    result += build_result
                    if len(build_result.installables):
                        built_stage.append((package, build_result.installables[0]))

                failed = self._install_stage(built_stage)
                result.failed_packages += failed

                _logger.debug("Done with current level: %s", level)
        return result

    def build_package(self, package: ROSPackage) -> BuildResult:
        _logger.info("Building: %s", package.name)
        make_target = self._make_target(package)
        build_target = self._dist_folder / make_target.name

        if self._overwrite:
            _logger.debug("Removing potentially existing deb-file: %s", str(build_target))
            build_target.unlink(missing_ok=True)

        result = BuildResult()
        if not build_target.exists():
            try:
                self.clear_package_cache(package)
                self._make_makefile(package)
                self._run_build(package)
                make_target.rename(build_target)
                self.clear_package_cache(package)
                installable = Installable(package.name, self._resolve_deb_name(package), build_target)
                result.installables.append(installable)
                result.missing_launch_files.append(self._checker.get_missing_launch_files(package, installable))
                _logger.info("Building done: %s", package.name)
            except (CommandAbortedError, CommandFailedError) as e:
                _logger.error("Building %s failed", package.name)  # noqa: TRY400
                result.failed_packages.append(package.name)
                write_log(self._robenv.path, package.name, e.output)
                if not self._can_fail:
                    raise
        else:
            _logger.info("Build %s skipped. Deb file exist.", package.name)

        return result

    def _install_stage(
        self,
        built_stage: list[tuple[ROSPackage, Installable]],
    ) -> list[PackageName]:
        failed_packages = []

        for package, installable in built_stage:
            try:
                _logger.info("installing: %s", installable.deb_name)
                self._robenv.install(installable, overwrite=self._overwrite, check_dependencies=False)
                _logger.info("install %s was successful", installable.deb_name)
            except (CommandAbortedError, CommandFailedError) as e:  # noqa: PERF203
                _logger.exception("install %s failed", package.name)
                failed_packages.append(package.name)
                write_log(self._robenv.path, package.name, e.output)
                if not self._can_fail:
                    raise

        return failed_packages

    def _make_target(self, package: ROSPackage) -> Path:
        return (package.path / ".." / self._resolve_deb_name(package)).resolve()

    def _run_build(self, package: ROSPackage) -> None:
        self._robenv.shell.run(
            "fakeroot debian/rules binary",
            cwd=package.path,
        )

        make_target = self._make_target(package)
        if package.is_metapackage():
            root_path = package.path / f"debian/ros-{self._robenv.ros_distro}-{package.name.replace('_', '-')}"
            deb_path = root_path.with_suffix(".deb")

            ros_root = root_path / f"opt/ros/{self._robenv.ros_distro}"

            distro_config = get_distro_config(self._robenv.ros_distro)
            for file in distro_config.meta_package_prevent_overwrite:
                (ros_root / file).unlink(missing_ok=True)

            self._robenv.shell.run(
                f"dpkg-deb --build --root-owner-group {root_path}",
                cwd=package.path,
            )
            make_target.unlink()
            deb_path.rename(make_target)

    def _make_makefile(self, package: ROSPackage) -> None:
        distro = self._robenv.ros_distro

        self._robenv.shell.run(
            f"bloom-generate rosdebian --ros-distro {distro} .",
            cwd=package.path,
            events={
                "Continue [Y/n]?": "n\r",
            },
        )

        makefile = package.path / "debian" / "rules"

        makefile.write_text(
            makefile.read_text()
            .replace(
                f"PKG_CONFIG_PATH=/opt/ros/{distro}/lib/pkgconfig",
                f"PKG_CONFIG_PATH={self._robenv.path!s}/opt/ros/{distro}/lib/pkgconfig",
            )
            .replace(
                f'CMAKE_PREFIX_PATH="/opt/ros/{distro}"',
                f'CMAKE_PREFIX_PATH="{self._robenv.path!s}/opt/ros/{distro}"',
            )
            .replace(
                f"/opt/ros/{distro}/setup.sh",
                f"{self._robenv.path!s}/opt/ros/{distro}/setup.sh",
            ),
        )

    @staticmethod
    @lru_cache
    def _resolve_system_code_name() -> str:
        for line in Path("/etc/os-release").read_text().splitlines():
            if line.startswith("VERSION_CODENAME"):
                return line.split("=")[1]

        return "focal"

    def _resolve_deb_name(self, package: ROSPackage) -> DebName:
        return DebName(
            f"{self._robenv.rosdep.resolve(package.name)}_{package.version}-0{Builder._resolve_system_code_name()}_amd64.deb",
        )
