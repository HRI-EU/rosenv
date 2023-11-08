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

import os

from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from cleo.application import Application
from cleo.testers.command_tester import CommandTester

from rosenv.environment.shell import RosEnvShell
from tests.conftest import YieldFixture


@pytest.fixture()
def spawn_mock() -> YieldFixture[MagicMock]:
    with patch.object(RosEnvShell, "spawn", autospec=True) as spawn:
        yield spawn


@pytest.fixture()
def _simulate_env() -> YieldFixture[None]:
    os.environ["ROSENV_ENV"] = "/test/path/to/rosenv"

    yield

    del os.environ["ROSENV_ENV"]


def test_shell_should_spawn_a_shell_process(
    init_app: Application,
    spawn_mock: MagicMock,
) -> None:
    assert not spawn_mock.called

    CommandTester(init_app.find("shell")).execute()

    assert spawn_mock.call_count == 1


def test_shell_should_return_spawn_return_code(
    init_app: Application,
    spawn_mock: MagicMock,
) -> None:
    expected_exit_code = 8
    spawn_mock.return_value = expected_exit_code

    assert not spawn_mock.called

    ret = CommandTester(init_app.find("shell")).execute()

    assert ret == expected_exit_code
    assert spawn_mock.call_count == 1


@pytest.mark.usefixtures("_simulate_env")
def test_shell_should_detect_if_running_already_in_rosenv(
    init_app: Application,
    spawn_mock: MagicMock,
) -> None:
    assert not spawn_mock.called

    ret = CommandTester(init_app.find("shell")).execute()

    assert ret == 0
    assert not spawn_mock.called
