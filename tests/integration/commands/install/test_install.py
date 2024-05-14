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
from unittest.mock import MagicMock

import pytest

from cleo.application import Application
from cleo.testers.command_tester import CommandTester

from robenv.environment.run_command import CommandFailedError
from tests.conftest import ROS_1
from tests.conftest import get_ros_version
from tests.integration.commands import create_cache_files_in_adder_project


def _get_adder_lib_location(robenv_target_path: Path) -> Path:
    if get_ros_version() == ROS_1:
        return robenv_target_path / "opt/ros/noetic/lib/libadder.so"

    return robenv_target_path / "opt/ros/iron/lib/x86_64-linux-gnu/libadder.a"


def _get_adder_header_location(robenv_target_path: Path) -> Path:
    if get_ros_version() == ROS_1:
        return robenv_target_path / "opt/ros/noetic/include/adder/adder.h"

    return robenv_target_path / "opt/ros/iron/include/adder/adder.h"


def _get_adder_deb_name() -> str:
    if get_ros_version() == ROS_1:
        return "ros-noetic-adder_0.0.0-0focal_amd64.deb"

    return "ros-iron-adder_0.0.0-0jammy_amd64.deb"


def build_and_install(app: Application, robenv_target_path: Path, ros_workspace_path: Path, dist_path: Path) -> None:
    debian_folder_path = ros_workspace_path / "adder" / "debian"
    obj_cache_path = ros_workspace_path / "adder" / ".obj-x86_64-linux-gnu"

    deb_name = _get_adder_deb_name()
    packages_folder = robenv_target_path / "robenv/packages"
    assert not packages_folder.exists()
    header = _get_adder_header_location(robenv_target_path)
    assert not header.exists()
    lib = _get_adder_lib_location(robenv_target_path)
    assert not lib.exists()

    create_cache_files_in_adder_project(ros_workspace_path)
    assert debian_folder_path.exists()
    assert obj_cache_path.exists()

    CommandTester(app.find("install")).execute(f"src --dist-folder={dist_path.name}")

    assert not debian_folder_path.exists()
    assert not obj_cache_path.exists()

    assert (dist_path / deb_name).exists()
    assert (packages_folder / deb_name).exists()
    assert header.exists()
    assert lib.exists()


def build_and_install_overwrite(app: Application, robenv_target_path: Path, dist_path: Path) -> None:
    header = _get_adder_header_location(robenv_target_path)
    assert header.exists()
    header_creation_timestamp = header.stat().st_ctime
    build_artifact = dist_path / _get_adder_deb_name()
    assert build_artifact.exists()
    artifact_creation_timestamp = build_artifact.stat().st_ctime

    CommandTester(app.find("install")).execute(f"src --dist-folder={dist_path.name}")

    assert header.exists()
    header_recreate_timestamp = header.stat().st_ctime
    assert header_recreate_timestamp > header_creation_timestamp
    assert build_artifact.exists()
    artifact_recreate_timestamp = build_artifact.stat().st_ctime
    assert artifact_recreate_timestamp > artifact_creation_timestamp


def build_and_install_no_overwrite(app: Application, robenv_target_path: Path, dist_path: Path) -> None:
    dist_path = Path("dist")
    header = _get_adder_header_location(robenv_target_path)
    assert header.exists()
    header_creation_timestamp = header.stat().st_ctime
    build_artifact = dist_path / _get_adder_deb_name()
    assert build_artifact.exists()
    artifact_creation_timestamp = build_artifact.stat().st_ctime

    CommandTester(app.find("install")).execute(f"src --dist-folder={dist_path.name} --no-overwrite")

    assert header.exists()
    header_no_overwrite_timestamp = header.stat().st_ctime
    assert header_no_overwrite_timestamp == header_creation_timestamp
    assert build_artifact.exists()
    artifact_no_overwrite_timestamp = build_artifact.stat().st_ctime
    assert artifact_no_overwrite_timestamp == artifact_creation_timestamp


def build_and_install_fails(app: Application, robenv_target_path: Path, run_mock: MagicMock, dist_path: Path) -> None:
    run_mock.return_value = 1, "cool output"
    run_mock.side_effect = CommandFailedError(command="command", exit_status=1, output="cool output")

    header = _get_adder_header_location(robenv_target_path)
    assert header.exists()
    header_creation_timestamp = header.stat().st_ctime
    with pytest.raises(CommandFailedError):
        CommandTester(app.find("install")).execute(f"src --dist-folder={dist_path.name}")

    assert header.exists()
    header_recreate_timestamp = header.stat().st_ctime
    assert header_recreate_timestamp == header_creation_timestamp


def build_and_install_can_fail(
    app: Application,
    robenv_target_path: Path,
    run_mock: MagicMock,
    dist_path: Path,
) -> None:
    run_mock.return_value = 1, "cool output"
    run_mock.side_effect = CommandFailedError(command="command", exit_status=1, output="cool output")

    header = _get_adder_header_location(robenv_target_path)
    assert header.exists()
    header_creation_timestamp = header.stat().st_ctime
    # The command would raise CommandFailedError, but with --can-fail we catch them and go on with the next package
    # For the error case see build_and_install_fails
    CommandTester(app.find("install")).execute(f"src --dist-folder={dist_path.name} --can-fail")

    assert header.exists()
    header_recreate_timestamp = header.stat().st_ctime
    assert header_recreate_timestamp == header_creation_timestamp


@pytest.mark.usefixtures(
    "rosdep_resolve_mock",
    "_copy_minimal_example_project",
)
def test_install_should_install_workspace(
    init_app: Application,
    robenv_target_path: Path,
    run_mock: MagicMock,
    dist_path: Path,
    ros_workspace_path: Path,
) -> None:
    build_and_install(init_app, robenv_target_path, ros_workspace_path, dist_path)
    build_and_install_overwrite(init_app, robenv_target_path, dist_path)
    build_and_install_no_overwrite(init_app, robenv_target_path, dist_path)
    build_and_install_fails(init_app, robenv_target_path, run_mock, dist_path)
    build_and_install_can_fail(init_app, robenv_target_path, run_mock, dist_path)
