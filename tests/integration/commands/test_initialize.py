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
from unittest.mock import ANY
from unittest.mock import MagicMock
from unittest.mock import call

import yaml

from cleo.application import Application
from cleo.testers.command_tester import CommandTester


def test_initialize_should_initialize_a_correct_rosenv(app: Application, rosenv_target_path: Path) -> None:
    command_tester = CommandTester(app.find("init"))
    command_tester.execute()

    assert rosenv_target_path.is_dir()
    assert (rosenv_target_path / "activate").is_file()
    assert (rosenv_target_path / "rosdep.yaml").is_file()

    rosdep_sources = rosenv_target_path / "etc/ros/rosdep/sources.list.d"
    assert rosdep_sources.is_dir()
    assert (rosdep_sources / "50-rosenv.list").is_file()


def test_initialize_should_initialize_rosdep(
    app: Application,
    run_mock: MagicMock,
) -> None:
    run_mock.return_value = 0, "cool output"
    run_mock.side_effect = None

    command_tester = CommandTester(app.find("init"))
    command_tester.execute()

    run_mock.assert_has_calls(
        [
            call(ANY, "rosdep init", Path.cwd()),
            call(ANY, "rosdep update", Path.cwd()),
        ],
    )


def test_rosdep_content_from_example(
    app: Application,
    rosenv_target_path: Path,
    example_project: Path,
    project_list: list[str],
) -> None:
    command = app.find("init")
    command_tester = CommandTester(command)
    command_tester.execute(f"--workspace-path {example_project!s}")

    assert (rosenv_target_path / "rosdep.yaml").is_file()

    rosdep_content: dict[str, dict[str, list[str]]] = yaml.safe_load((rosenv_target_path / "rosdep.yaml").read_text())
    result_keys = list(rosdep_content.keys())
    assert result_keys == project_list


def test_rosdep_set_file(
    app: Application,
    rosenv_target_path: Path,
) -> None:
    location = "some_random_location"
    rosdep_file_path = rosenv_target_path.parent / location / "rosdep.yaml"

    rosdep_file_path.parent.mkdir(exist_ok=True, parents=True)
    rosdep_file_path.write_text(
        """
adder:
  ubuntu:
  - ros-noetic-adder
""",
    )

    # execute init
    command = app.find("init")
    command_tester = CommandTester(command)
    command_tester.execute(f"--rosdep-path {rosdep_file_path!s}")

    # check for correct location entry of rosdep in 50-rosenv.list
    rosdep_sources = rosenv_target_path / "etc/ros/rosdep/sources.list.d"
    rosdep_sources_list = rosdep_sources / "50-rosenv.list"

    assert rosdep_sources.is_dir()
    assert rosdep_sources_list.is_file()

    assert str(rosdep_file_path) in rosdep_sources_list.read_text()
