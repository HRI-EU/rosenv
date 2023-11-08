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

import shlex
import shutil
import signal

from pathlib import Path
from typing import Any
from typing import Literal

import pexpect

from shellingham import detect_shell

from rosenv.environment.run_command import CommandOutput
from rosenv.environment.run_command import run_command


class UnsupportedShellError(Exception):
    def __init__(self, shell: str) -> None:
        super().__init__(f"Shell '{shell}' is currently not supported by rosenv")


SupportedShell = Literal["sh", "bash", "zsh"]


class RosEnvShell:
    def __init__(self, activate_script: Path) -> None:
        self._activate_script = activate_script

    def _get_activate_script(self, shell_name: SupportedShell | None = None) -> Path:
        if shell_name is None:
            shell_name, _ = detect_shell()

        return self._activate_script.with_suffix(f".{shell_name}")

    def run(
        self,
        command: str,
        cwd: Path | None = None,
        events: dict[str, str] | None = None,
    ) -> CommandOutput:
        return run_command(self.command_in_env(command), events=events, cwd=cwd)

    def command_in_env(self, command: str) -> str:
        return f"bash -c 'source {self._get_activate_script('bash')!s} && {command}'"

    def spawn(self) -> int:
        shell = self._get_shell()

        def resize(_: Any, __: Any) -> None:  # noqa: ANN401
            terminal = shutil.get_terminal_size()
            shell.setwinsize(terminal.lines, terminal.columns)

        signal.signal(signal.SIGWINCH, resize)

        shell.interact(escape_character=None)
        shell.close()

        exit_code: int = shell.exitstatus
        return exit_code

    def _get_shell(self) -> pexpect.spawn:
        shell_name, shell_path = detect_shell()
        terminal = shutil.get_terminal_size()

        if shell_name not in ("zsh", "bash", "sh"):
            raise UnsupportedShellError(shell_name)

        shell = pexpect.spawn(
            shell_path,
            ["-i"],
            dimensions=(terminal.lines, terminal.columns),
        )
        shell.sendline(f"source {shlex.quote(str(self._get_activate_script()))}")

        return shell
