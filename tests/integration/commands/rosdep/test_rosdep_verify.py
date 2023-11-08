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

from rosenv.environment.run_command import CommandFailedError
from rosenv.environment.run_command import CommandOutput
from rosenv.environment.shell import RosEnvShell


@pytest.mark.usefixtures("_copy_full_example_project")
def test_rosdep_verify_should_verify_successfully(init_app: Application) -> None:
    assert CommandTester(init_app.find("rosdep verify")).execute() == 0


@pytest.mark.usefixtures("_copy_full_example_project")
def test_rosdep_verify_should_exit_with_non_zero_code(init_app: Application, run_mock: MagicMock) -> None:
    orig_side_effect = run_mock.side_effect

    def additional_effect(
        self: RosEnvShell,
        command: str,
        cwd: Path,
        events: dict[str, str] | None = None,
    ) -> CommandOutput:
        if "rosdep resolve" in command:
            raise CommandFailedError(command, 1, "Unresolvable")

        return orig_side_effect(self, command, cwd, events)  # type: ignore[no-any-return]

    run_mock.side_effect = additional_effect

    exit_code = CommandTester(init_app.find("rosdep verify")).execute()

    assert exit_code != 0
