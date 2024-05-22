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

from typing import ClassVar

from cleo.application import Application
from cleo.io.io import IO
from cleo.io.outputs.output import Verbosity


# additional loglevel under logging.DEBUG
LOGLEVEL_TRACE = 5
LOGLEVEL_FINE = 3

ROBENV_FILTER = logging.Filter("robenv")


def _io_to_level(io: IO) -> int:
    if io.is_debug():
        return LOGLEVEL_FINE

    if io.is_very_verbose():
        return LOGLEVEL_TRACE

    if io.is_verbose():
        return logging.DEBUG

    if io.output.is_quiet():
        return logging.WARNING

    return logging.INFO


class IOFormatter(logging.Formatter):
    _colors: ClassVar[dict[int, str]] = {
        logging.INFO: "info",
        logging.WARNING: "fg=yellow",
        logging.ERROR: "error",
    }

    def format(self, record: logging.LogRecord) -> str:
        if not record.exc_info:
            level = record.levelno
            msg = record.msg

            if level in self._colors:
                msg = f"<{self._colors[level]}>{msg}</>"

            record.msg = msg

        if not ROBENV_FILTER.filter(record):
            # prefix third-party packages with name for easier debugging
            record.msg = f"[{record.name}] {record.msg}"

        return super().format(record)


class CleoLogHandler(logging.Handler):
    _log_levels: ClassVar[dict[int, Verbosity]] = {
        LOGLEVEL_FINE: Verbosity.DEBUG,
        LOGLEVEL_TRACE: Verbosity.VERY_VERBOSE,
        logging.DEBUG: Verbosity.VERBOSE,
    }

    def __init__(self, io: IO) -> None:
        self._io = io
        super().__init__()

    def _level_to_verbosity(self, level: int) -> Verbosity:
        return self._log_levels.get(level, Verbosity.NORMAL)

    def emit(self, record: logging.LogRecord) -> None:
        msg = self.format(record)

        self._io.write_line(
            msg,
            verbosity=self._level_to_verbosity(record.levelno),
        )


def configure_logging(app: Application) -> Application:
    io = app.create_io()
    # app doesn't expose this method for some reason, but otherwise we only
    # have a "configured" io in the commands and would need to do the logging
    # config in every command again
    app._configure_io(io)  # noqa: SLF001

    handler = CleoLogHandler(io)
    handler.setFormatter(IOFormatter())

    if not io.is_very_verbose():
        handler.addFilter(ROBENV_FILTER)

    level = _io_to_level(io)
    logging.basicConfig(
        format="%(message)s",
        level=level,
        handlers=[handler],
    )

    return app
