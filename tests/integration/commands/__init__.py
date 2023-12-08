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

from rosenv.environment.distro import RosDistribution


class MockResponse:
    def __init__(self, content: bytes) -> None:
        self.content = content


def package_name() -> str:
    return "adder"


def _get_rosenv_paths(rosenv_target_path: Path, ros_distro: RosDistribution) -> tuple[Path, Path, Path]:
    packages_folder = rosenv_target_path / "rosenv/packages"
    header = rosenv_target_path / f"opt/ros/{ros_distro}/include/{package_name()}/{package_name()}.h"
    lib = rosenv_target_path / f"opt/ros/{ros_distro}/lib/lib{package_name()}.so"
    return header, lib, packages_folder


def assert_is_not_installed(rosenv_target_path: Path, deb_name: str, ros_distro: RosDistribution) -> None:
    _, _, packages_folder = _get_rosenv_paths(rosenv_target_path, ros_distro)
    assert not (packages_folder / deb_name).exists()


def assert_is_installed(rosenv_target_path: Path, deb_name: str, ros_distro: RosDistribution) -> None:
    _, _, packages_folder = _get_rosenv_paths(rosenv_target_path, ros_distro)
    assert (packages_folder / deb_name).exists()


def get_adder_workspace_paths(ros_workspace_path: Path) -> tuple[Path, Path]:
    return ros_workspace_path / "adder" / "debian", ros_workspace_path / "adder" / ".obj-x86_64-linux-gnu"


def assert_adder_build_cache_files_exist(ros_workspace_path: Path) -> None:
    def check(base: Path) -> None:
        assert base.exists()
        assert (base / "nice_file").exists()
        assert (base / "nice_folder_name").exists()
        assert (base / "nice_folder_name" / "cool_file").exists()

    debian_folder_path, obj_cache_path = get_adder_workspace_paths(ros_workspace_path)
    check(debian_folder_path)
    check(obj_cache_path)


def assert_adder_build_cache_files_not_exist(ros_workspace_path: Path) -> None:
    def check(base: Path) -> None:
        assert not base.exists()
        assert not (base / "nice_file").exists()
        assert not (base / "nice_folder_name").exists()
        assert not (base / "nice_folder_name" / "cool_file").exists()

    debian_folder_path, obj_cache_path = get_adder_workspace_paths(ros_workspace_path)
    check(debian_folder_path)
    check(obj_cache_path)


def create_cache_files_in_adder_project(ros_workspace_path: Path) -> None:
    def create(base: Path) -> None:
        base.mkdir()
        (base / "nice_file").touch()
        (base / "nice_folder_name").mkdir()
        (base / "nice_folder_name" / "cool_file").touch()

    debian_folder_path, obj_cache_path = get_adder_workspace_paths(ros_workspace_path)
    create(debian_folder_path)
    create(obj_cache_path)
