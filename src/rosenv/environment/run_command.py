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

from logging import getLogger
from pathlib import Path
from signal import SIGTERM

from pexpect.exceptions import EOF
from pexpect.exceptions import TIMEOUT
from pexpect.pty_spawn import spawn

from rosenv.logging import LOGLEVEL_TRACE
from rosenv.util.cancelable_executor import CancelableExecutor


_logger = getLogger(__name__)

ExitStatus = int
CommandOutput = str


class CommandFailedError(Exception):
    def __init__(self, command: str, exit_status: ExitStatus, output: str) -> None:
        super().__init__(f"Command `{command}` failed with exit code {exit_status}:\r\n{output}")
        self.command = command
        self.exit_status = exit_status
        self.output = output


class CommandAbortedError(Exception):
    def __init__(self, command: str, output: str) -> None:
        super().__init__(f"Command `{command}` aborted:\r\n{output}")
        self.command = command
        self.output = output


def _cleanup(child: spawn) -> None:
    if child.isalive():
        _logger.debug("Child was still alive")
        child.kill(sig=SIGTERM)


def _handle_interrupt(
    command: str,
    child: spawn,
    child_output_list: list[str],
    cause: BaseException | None = None,
) -> None:
    _logger.debug("Command was interrupted")

    if child.before is not None:
        child_output_list.append(child.before)

    output = child.string_type().join(child_output_list).decode()
    _cleanup(child)
    raise CommandAbortedError(command=command, output=output) from cause


def _handle_timeout(child: spawn, len_output: int) -> int:
    buffer = child.before
    len_before = len(buffer)
    if len_before > len_output:
        _logger.log(
            level=LOGLEVEL_TRACE,
            msg=buffer[len_output:len_before].decode(),
        )
    return len_before


def run_command(
    command: str,
    maxread: int = 2000,
    events: dict[str, str] | None = None,
    cwd: Path | None = None,
) -> CommandOutput:
    with spawn(
        command,
        timeout=1,
        maxread=maxread,
        cwd=str(cwd.resolve()) if cwd is not None else None,
    ) as child:
        child_output_list: list[str] = []
        patterns: list[str] | None = None
        responses: list[str] | None = None
        _logger.debug("Command: %s", command)
        len_output = 0
        if events is not None and len(events) > 0:
            patterns = list(events.keys())
            responses = list(events.values())

        while True:
            try:
                if CancelableExecutor.cancel_event.is_set():
                    _handle_interrupt(command, child, child_output_list)

                index = child.expect(patterns)

                if isinstance(child.after, str):
                    child_output_list.append(child.before + child.after)
                else:
                    # child.after may have been a TIMEOUT or EOF,
                    # which we don't want appended to the list.
                    child_output_list.append(child.before)

                if responses is not None and isinstance(responses[index], str):
                    child.send(responses[index])
            except EOF as e:  # noqa: PERF203
                child_output_list.append(child.before)
                output: str = child.string_type().join(child_output_list).decode()
                _cleanup(child)
                _logger.debug("Command ended: cmd=%s | status=%s", command, child.exitstatus)

                if child.exitstatus == 0:
                    return output

                raise CommandFailedError(
                    command=command,
                    exit_status=child.exitstatus,
                    output=output,
                ) from e
            except TIMEOUT:
                len_output = _handle_timeout(child, len_output)
            except KeyboardInterrupt as e:
                _handle_interrupt(command, child, child_output_list, e)
