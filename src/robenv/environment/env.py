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

import errno
import os
import shutil

from collections import defaultdict
from concurrent.futures import as_completed
from dataclasses import dataclass
from functools import lru_cache
from itertools import chain
from logging import getLogger
from pathlib import Path
from typing import Dict
from typing import Iterator
from typing import Mapping
from typing import NewType
from typing import TypedDict

import yaml

from deb_pkg_tools.deps import AbstractRelationship
from deb_pkg_tools.deps import parse_depends
from deb_pkg_tools.package import ArchiveEntry
from deb_pkg_tools.package import PackageFile
from deb_pkg_tools.package import collect_related_packages
from deb_pkg_tools.package import inspect_package_contents
from deb_pkg_tools.package import parse_filename
from deb_pkg_tools.utils import find_installed_version

from robenv.environment.distro import RosDistribution
from robenv.environment.distro import parse_distro
from robenv.environment.locate import locate
from robenv.environment.run_command import CommandAbortedError
from robenv.environment.run_command import CommandFailedError
from robenv.environment.shell import RobEnvShell
from robenv.ros_package.package import PackageName
from robenv.rosdep.rosdep import ResolvedPackageName
from robenv.rosdep.rosdep import Rosdep
from robenv.util.cancelable_executor import CancelableExecutor
from robenv.util.cpu_count import get_cpu_count
from robenv.util.paths import remove_slash_prefix


_logger = getLogger(__name__)

DEFAULT_ROBENV_NAME = "robenv"

DebName = NewType("DebName", str)


@dataclass()
class Installable:
    name: PackageName
    deb_name: DebName
    location: Path


class UnmetDependencyError(Exception):
    def __init__(self, package: str, missing_dependencies: list[AbstractRelationship]) -> None:
        super().__init__(
            f"{package} dependencies not found: {', '.join([str(dependency) for dependency in missing_dependencies])}",
        )


@lru_cache
def _get_installed_files(robenv_path: Path, deb_path: Path) -> list[Path]:
    contents = inspect_package_contents(str(deb_path))
    return [robenv_path / remove_slash_prefix(file) for file in contents]


class PackageIsNotInstalledError(Exception):
    def __init__(self, package: str) -> None:
        super().__init__(f"Package {package} is not installed")


class RemoveDependencyError(Exception):
    def __init__(self, package: str, dependent_packages: list[PackageName]) -> None:
        super().__init__(
            f"Removing of Package {package} prohibited. {package} is a dependency for: {dependent_packages}",
        )


class FileAlreadyInstalledError(Exception):
    def __init__(self, file: Path, installed_by_packages: list[PackageName]) -> None:
        self.file = file
        self.installed_by_packages = installed_by_packages
        super().__init__(f"{file} already installed by {installed_by_packages}")


InstalledPackages = Dict[PackageName, Path]


class SettingsFile(TypedDict):
    installed_packages: dict[PackageName, str]
    ros_distro: str


class RobEnvSettings:
    def __init__(
        self,
        settings_file: Path,
        installed_packages: InstalledPackages,
        ros_distro: RosDistribution,
    ) -> None:
        self._settings_file = settings_file
        self.installed_packages = installed_packages
        self.ros_distro: RosDistribution = ros_distro

    @classmethod
    def read(cls, robenv_path: Path) -> RobEnvSettings:
        settings_file = cls.get_settings_path(robenv_path)
        settings: SettingsFile = yaml.safe_load(settings_file.read_text())
        installed_packages = {key: Path(value) for key, value in settings["installed_packages"].items()}
        ros_distro = parse_distro(settings["ros_distro"])
        return cls(
            settings_file=settings_file,
            installed_packages=installed_packages,
            ros_distro=ros_distro,
        )

    @staticmethod
    def initialize(robenv_path: Path, ros_distro: RosDistribution) -> None:
        RobEnvSettings(
            settings_file=RobEnvSettings.get_settings_path(robenv_path),
            installed_packages={},
            ros_distro=ros_distro,
        ).save()

    @staticmethod
    def get_settings_path(robenv_path: Path) -> Path:
        return robenv_path / "robenv/settings.yaml"

    def save(self) -> None:
        if not self._settings_file.exists():
            self._settings_file.parent.mkdir(parents=True, exist_ok=True)

        self._settings_file.write_text(yaml.safe_dump(self._as_dict()))

    def add_installed(self, name: PackageName, location: Path) -> None:
        self.installed_packages[name] = location.absolute()
        self.save()

    def _as_dict(self) -> SettingsFile:
        return {
            "installed_packages": {key: str(value) for key, value in self.installed_packages.items()},
            "ros_distro": self.ros_distro,
        }

    def remove_installed(self, name: PackageName) -> None:
        self.installed_packages[name].unlink()
        del self.installed_packages[name]
        self.save()


class RobEnv:
    def __init__(self) -> None:
        self.path = locate(DEFAULT_ROBENV_NAME)
        # TODO(Moritz): /opt/ros/noetic is only correct if venv was created with default ros-path
        # https://dmz-gitlab.honda-ri.de/SSE/robenv/-/issues/28
        self._settings = RobEnvSettings.read(self.path)
        self.shell = RobEnvShell(self.path / f"opt/ros/{self._settings.ros_distro}/setup.sh")
        self._rosdep: Rosdep | None = None

    @property
    def rosdep(self) -> Rosdep:
        if self._rosdep is None:
            self._rosdep = Rosdep(self.path, self.shell)
        return self._rosdep

    @property
    def ros_distro(self) -> RosDistribution:
        return self._settings.ros_distro

    @property
    def _packages_path(self) -> Path:
        return self.path / "robenv/packages/"

    @property
    def _install_path(self) -> Path:
        return self.path

    def _copy(self, installable: Installable) -> Path:
        self._packages_path.mkdir(parents=True, exist_ok=True)

        saved_package = self._packages_path / installable.deb_name
        shutil.copy(installable.location, saved_package)
        return saved_package.resolve()

    def is_installed(self, package_name: PackageName) -> bool:
        return package_name in self._settings.installed_packages

    def get_package_deb_path(self, package_name: PackageName) -> Path:
        return self._settings.installed_packages[package_name]

    def get_installed_packages(self) -> list[PackageName]:
        return list(self._settings.installed_packages.keys())

    @staticmethod
    def _is_dependency(resolved_package_name: ResolvedPackageName, dependent: Path) -> bool:
        return any(package.name == resolved_package_name for package in collect_related_packages(dependent))

    def _get_dependent_packages(self, dependency_package: PackageName) -> list[PackageName]:
        resolved_package_name = self.rosdep.resolve(package_name=dependency_package)

        with CancelableExecutor(max_workers=get_cpu_count(minimum=4)) as pool:
            futures = {
                pool.submit(self._is_dependency, resolved_package_name, path_to_debian): package_name
                for package_name, path_to_debian in self._settings.installed_packages.items()
            }

            return [futures[future] for future in as_completed(futures) if future.result()]

    @staticmethod
    def _re_init_symlinked_dir(folder: Path) -> None:
        source_path = Path(os.readlink(folder.absolute()))
        folder.unlink()
        folder.mkdir()
        _logger.debug("reinit symlinks one level below for folder: %s", folder)
        for source in source_path.iterdir():
            target = folder / source.name
            _logger.debug("creating symlink: %s -> %s", target, source)
            target.symlink_to(source, target_is_directory=source.is_dir())

    def _to_robenv_root_absolute(self, file: Path | str) -> Path:
        return self._install_path / remove_slash_prefix(file)

    def _build_package_file_lookup(self) -> dict[Path, list[PackageName]]:
        lookup = defaultdict(list)
        inspection_items = (
            (file_path, package)
            for package, deb_path in self._settings.installed_packages.items()
            for file_path in _get_installed_files(self._install_path, deb_path)
        )
        for path, package in inspection_items:
            lookup[path].append(package)

        return lookup

    def _find_installed_by_packages(self, file: Path) -> list[PackageName]:
        files_installed_by_package = self._build_package_file_lookup()
        return files_installed_by_package[file]

    def _handle_package_contents(self, installable: Installable, *, overwrite: bool) -> None:
        contents: dict[str, ArchiveEntry] = inspect_package_contents(str(installable.location))
        for package_path in contents:
            installed_file_path = self._to_robenv_root_absolute(package_path)
            _logger.debug(
                "Trying to install: installed_file_path=%s package_path=%s symlink:%s",
                installed_file_path,
                package_path,
                contents[package_path].target,
            )
            if installed_file_path.is_file():
                installed_by = self._find_installed_by_packages(installed_file_path)
                if overwrite:
                    _logger.warning(
                        "File exists in robenv, will be overwritten: %s installed by %s",
                        str(installed_file_path.relative_to(self.path)),
                        installed_by,
                    )
                else:
                    raise FileAlreadyInstalledError(installed_file_path, installed_by)
            elif installed_file_path.is_symlink() and contents[package_path].target == "":
                _logger.debug("Symlinked dir exists in robenv: %s", str(installed_file_path))
                self._re_init_symlinked_dir(installed_file_path)

    def _get_dependencies_of(
        self,
        installable: Installable,
    ) -> Iterator[AbstractRelationship]:
        return chain.from_iterable(
            parse_depends(self.shell.run(f"dpkg-deb -f {installable.location} {field}"))
            for field in ("depends", "pre-depends")
        )

    @staticmethod
    def _get_system_installed_version(dependency_name: str) -> str | None:
        return find_installed_version(dependency_name)  # type: ignore[no-any-return]

    def _get_robenv_installed_debs(self) -> Mapping[str, PackageFile]:
        if not self._packages_path.exists():
            return {}
        file_names = (parse_filename(filename) for filename in self._packages_path.iterdir())
        return {package_file.name: package_file for package_file in file_names}

    @staticmethod
    def _is_met_via_robenv(
        name: str,
        dependency: AbstractRelationship,
        robenv_installed_debs: Mapping[str, PackageFile],
    ) -> bool:
        return name in robenv_installed_debs and dependency.matches(
            name,
            robenv_installed_debs[name].version,
        )

    @staticmethod
    def _is_met_via_system(
        name: str,
        dependency: AbstractRelationship,
    ) -> bool:
        system_version = RobEnv._get_system_installed_version(name)

        # System dependencies MUST have a version. So if no version can be found, package is not installed
        return system_version is not None and dependency.matches(name, system_version)

    @staticmethod
    def _is_dependency_met(
        dependency: AbstractRelationship,
        robenv_installed_debs: Mapping[str, PackageFile],
    ) -> bool:
        _logger.debug("Checking dependency: %s", dependency)

        return any(
            RobEnv._is_met_via_robenv(alternative, dependency, robenv_installed_debs)
            or RobEnv._is_met_via_system(
                alternative,
                dependency,
            )
            for alternative in dependency.names
        )

    def _check_for_dependencies(self, installable: Installable) -> None:
        _logger.debug("Checking dependencies of %s", installable.name)
        robenv_installed_debs = self._get_robenv_installed_debs()

        unmet_dependencies = [
            dependency
            for dependency in self._get_dependencies_of(installable)
            if not RobEnv._is_dependency_met(dependency, robenv_installed_debs)
        ]

        if len(unmet_dependencies) != 0:
            raise UnmetDependencyError(installable.name, unmet_dependencies)

    def install(self, installable: Installable, *, overwrite: bool, check_dependencies: bool) -> None:
        package_name = installable.name

        if check_dependencies:
            self._check_for_dependencies(installable)

        if self.is_installed(package_name):
            if overwrite:
                _logger.info("Removing already installed package %s", package_name)
                self.uninstall(package_name, force=True)
            else:
                _logger.info("Skipping already installed package %s", package_name)
                return

        self._handle_package_contents(installable, overwrite=overwrite)

        package_file = self._copy(installable)
        _logger.debug("Installing package at %s", str(package_file))

        try:
            self.shell.run(f"/usr/bin/dpkg-deb --extract {package_file!s} {self._install_path!s}", cwd=Path.cwd())
        except (CommandAbortedError, CommandFailedError):
            package_file.unlink()
            raise

        self._settings.add_installed(package_name, package_file)

    def uninstall(self, package_name: PackageName, *, force: bool = False) -> None:
        if not self.is_installed(package_name):
            raise PackageIsNotInstalledError(package_name)

        if not force:
            dependents = self._get_dependent_packages(package_name)
            if len(dependents) > 0:
                raise RemoveDependencyError(package_name, dependents)

        _logger.debug("Uninstalling package: %s", package_name)

        contents: dict[str, ArchiveEntry] = inspect_package_contents(
            str(self._settings.installed_packages[package_name]),
        )
        _logger.debug("Package Content: %s", contents)

        for package_path in reversed(contents):
            # We need to go bottom-up here, as we maybe empty folders which we
            # can then delete; all packages that I've seen so far had the
            # top-down order so reversed should be bottom-up
            sanitized_path = remove_slash_prefix(package_path)
            installed_file_path = self._install_path / sanitized_path

            _logger.debug(
                "Trying to delete: installed_file_path=%s sanitized_path=%s package_path=%s",
                installed_file_path,
                sanitized_path,
                package_path,
            )

            if not installed_file_path.exists():
                _logger.warning("File doesn't exist but was installed: %s", str(installed_file_path))
                continue

            if installed_file_path.is_dir():
                try:
                    installed_file_path.rmdir()
                except OSError as e:
                    if e.errno != errno.ENOTEMPTY:
                        # We only expect directories to not be empty, this is another error
                        raise

                    _logger.debug("Directory not empty, leaving it: %s", str(installed_file_path))
                continue

            _logger.debug("Removing: %s", installed_file_path)
            installed_file_path.unlink()
        self._settings.remove_installed(package_name)
