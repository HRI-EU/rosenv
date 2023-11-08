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

import logging
import shutil

from pathlib import Path

import pytest

from cleo.application import Application
from cleo.testers.command_tester import CommandTester
from deb_pkg_tools.package import ArchiveEntry
from deb_pkg_tools.package import inspect_package_contents

from tests.conftest import ROS_2
from tests.conftest import YieldFixture
from tests.conftest import get_ros_version


@pytest.fixture()
def _copy_success_launch_file_project(
    rosenv_target_path: Path,
    example_project_launch_files: Path,
) -> YieldFixture[None]:
    target_folder = rosenv_target_path.parent / "src"
    target_folder.mkdir(exist_ok=True, parents=True)

    failing_project = example_project_launch_files / "src/launch_success"

    assert failing_project.exists(), "Failing launch file project doesn't exist!"

    shutil.copytree(failing_project, target_folder / "launch_success")

    yield

    shutil.rmtree(target_folder, ignore_errors=True)


@pytest.fixture()
def _copy_failing_launch_file_project(
    rosenv_target_path: Path,
    example_project_launch_files: Path,
) -> YieldFixture[None]:
    target_folder = rosenv_target_path.parent / "src"
    target_folder.mkdir(exist_ok=True, parents=True)

    failing_project = example_project_launch_files / "src/launch_fails"

    assert failing_project.exists(), "Failing launch file project doesn't exist!"

    shutil.copytree(failing_project, target_folder / "launch_fails")

    yield

    shutil.rmtree(target_folder, ignore_errors=True)


@pytest.mark.skipif(get_ros_version() == ROS_2, reason="Launchfile-Checks only work in ROS1 currently")
@pytest.mark.usefixtures(
    "rosdep_resolve_mock",
    "_copy_success_launch_file_project",
)
def test_launch_detection_should_not_error_and_contain_launch_files(
    init_app: Application,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.ERROR)
    dist_folder = Path("dist")

    assert not dist_folder.exists()
    CommandTester(init_app.find("install")).execute("src")
    assert dist_folder.exists()

    built_packages = list(dist_folder.iterdir())
    assert len(built_packages) == 1

    contents: dict[str, ArchiveEntry] = inspect_package_contents(built_packages[0])

    assert len(caplog.records) == 0
    assert any(file.endswith("/server.launch") for file in contents)


@pytest.mark.skipif(get_ros_version() == ROS_2, reason="Launchfile-Checks only work in ROS1 currently")
@pytest.mark.usefixtures(
    "rosdep_resolve_mock",
    "_copy_failing_launch_file_project",
)
def test_launch_detection_should_detect_missing_launch_file_and_log(
    init_app: Application,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.ERROR)
    dist_folder = Path("dist")

    assert not dist_folder.exists()
    command_tester = CommandTester(init_app.find("install"))
    command_tester.execute("src")
    assert dist_folder.exists()

    built_packages = list(dist_folder.iterdir())
    assert len(built_packages) == 1

    contents: dict[str, ArchiveEntry] = inspect_package_contents(built_packages[0])

    assert not any(file.endswith("/server.launch") for file in contents)

    expected_records = [
        ("rosenv.commands.install", logging.ERROR, "Missing launch files:"),
        ("rosenv.commands.install", logging.ERROR, "\tlaunch_fails:"),
        ("rosenv.commands.install", logging.ERROR, "\t\t- launch/server.launch"),
    ]

    assert len(caplog.records) == len(expected_records)
    assert caplog.record_tuples == expected_records


@pytest.mark.skipif(get_ros_version() == ROS_2, reason="Launchfile-Checks only work in ROS1 currently")
@pytest.mark.usefixtures(
    "rosdep_resolve_mock",
    "_copy_failing_launch_file_project",
)
def test_launch_detection_should_not_check_for_missing_launch_files(
    init_app: Application,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.ERROR)
    dist_folder = Path("dist")

    assert not dist_folder.exists()
    command_tester = CommandTester(init_app.find("install"))
    command_tester.execute("src --no-check-launchfiles")
    assert dist_folder.exists()

    built_packages = list(dist_folder.iterdir())
    assert len(built_packages) == 1

    contents: dict[str, ArchiveEntry] = inspect_package_contents(built_packages[0])

    assert not any(file.endswith("/server.launch") for file in contents)
    assert len(caplog.records) == 0
