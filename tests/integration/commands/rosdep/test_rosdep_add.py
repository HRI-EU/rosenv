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

import pytest

from cleo.application import Application
from cleo.testers.command_tester import CommandTester


def test_rosdep_add_should_add_system_dependency_to_rosdep_yaml(
    app: Application,
    rosdep_yaml: Path,
    translated_adder: str,
) -> None:
    CommandTester(app.find("rosdep add")).execute("dependency translation")

    assert (
        rosdep_yaml.read_text()
        == f"""\
adder:
  ubuntu:
  - {translated_adder}
dependency:
  ubuntu:
  - translation
"""
    )


def test_rosdep_add_should_add_pip_dependency_to_rosdep_yaml(
    app: Application,
    rosdep_yaml: Path,
    translated_adder: str,
) -> None:
    CommandTester(app.find("rosdep add")).execute("dependency translation --pip-dependency")

    assert (
        rosdep_yaml.read_text()
        == f"""\
adder:
  ubuntu:
  - {translated_adder}
dependency:
  ubuntu:
    pip:
      packages:
      - translation
"""
    )


@pytest.mark.usefixtures("_copy_minimal_example_project")
def test_rosdep_add_should_run_rosdep_update(
    init_app: Application,
    run_mock: MagicMock,
) -> None:
    # prevent side_effect running a second time
    run_mock.side_effect = None
    # has no side_effect argument as it's a 'autospec'ed mode
    run_mock.reset_mock()

    CommandTester(init_app.find("rosdep add")).execute("dependency translation --run-update")

    run_mock.assert_called_once_with(ANY, "rosdep update", Path.cwd())
