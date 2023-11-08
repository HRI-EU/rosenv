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

from pytest_mock import MockerFixture

from rosenv.environment.shell import RosEnvShell
from rosenv.environment.shell import UnsupportedShellError


@pytest.fixture()
def pexpect_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("rosenv.environment.shell.pexpect")


@pytest.fixture()
def run_command_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("rosenv.environment.shell.run_command")


@pytest.fixture()
def detect_shell_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("rosenv.environment.shell.detect_shell")


@pytest.fixture()
def terminal_size() -> MagicMock:
    size = MagicMock()
    size.lines = 1
    size.columns = 1
    return size


@pytest.fixture(autouse=True)
def shutil_mock(mocker: MockerFixture, terminal_size: MagicMock) -> MagicMock:
    mocked = mocker.patch("rosenv.environment.shell.shutil")
    mocked.get_terminal_size.return_value = terminal_size
    return mocked


@pytest.fixture()
def activate_script(tmp_path: Path) -> Path:
    return tmp_path / "opt/ros/noetic/setup.bash"


def test_run_command__calls_command_within_env(run_command_mock: MagicMock, activate_script: Path) -> None:
    test_command = "test_command"

    expected_command = f"bash -c 'source {activate_script} && {test_command}'"

    # run_command_mock.run.return_value = (b"test_output", expected_exit_status)

    sut = RosEnvShell(activate_script)
    sut.run(command=test_command, cwd=Path.cwd())

    assert run_command_mock.called
    run_command_mock.assert_called_once_with(
        expected_command,
        events=None,
        cwd=Path.cwd(),
    )


def test_get_shell__raises_on_unsupported_shell(
    activate_script: Path,
    detect_shell_mock: MagicMock,
    run_command_mock: MagicMock,
) -> None:
    detect_shell_mock.return_value = "unknown", "unknown"

    rosenv_shell = RosEnvShell(activate_script)

    with pytest.raises(UnsupportedShellError):
        rosenv_shell._get_shell()  # noqa: SLF001

    assert not run_command_mock.spawn.called


def test_get_shell__spawns_zsh_shell(
    activate_script: Path,
    detect_shell_mock: MagicMock,
    pexpect_mock: MagicMock,
    terminal_size: MagicMock,
) -> None:
    detect_shell_mock.return_value = "zsh", "/path/to/zsh"

    rosenv_shell = RosEnvShell(activate_script)

    shell = rosenv_shell._get_shell()  # noqa: SLF001

    assert pexpect_mock.spawn.called
    pexpect_mock.spawn.assert_called_once_with(
        "/path/to/zsh",
        ["-i"],
        dimensions=(terminal_size.lines, terminal_size.columns),
    )
    assert shell is pexpect_mock.spawn.return_value
    shell.sendline.assert_called_once_with(
        f"source {activate_script.with_suffix('.zsh')}",
    )


def test_get_shell__spawns_bash_shell(
    activate_script: Path,
    detect_shell_mock: MagicMock,
    terminal_size: MagicMock,
    pexpect_mock: MagicMock,
) -> None:
    detect_shell_mock.return_value = "bash", "/path/to/bash"

    rosenv_shell = RosEnvShell(activate_script)

    shell = rosenv_shell._get_shell()  # noqa: SLF001

    assert pexpect_mock.spawn.called
    pexpect_mock.spawn.assert_called_once_with(
        "/path/to/bash",
        ["-i"],
        dimensions=(terminal_size.lines, terminal_size.columns),
    )
    assert shell is pexpect_mock.spawn.return_value
    shell.sendline.assert_called_once_with(
        f"source {activate_script.with_suffix('.bash')}",
    )
