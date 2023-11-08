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

from importlib import metadata

from cleo.application import Application

from rosenv import __name__ as app_name
from rosenv.commands.add import AddCommand
from rosenv.commands.clear_cache import ClearCacheCommand
from rosenv.commands.info import InfoCommand
from rosenv.commands.initialize import InitRosenvCommand
from rosenv.commands.install import InstallCommand
from rosenv.commands.remove import RemoveCommand
from rosenv.commands.rosdep_add import RosdepAddCommand
from rosenv.commands.rosdep_generate import RosdepGenerateCommand
from rosenv.commands.rosdep_remove import RosdepRemoveCommand
from rosenv.commands.rosdep_verify import RosdepVerifyCommand
from rosenv.commands.run import RunCommand
from rosenv.commands.shell import ShellCommand
from rosenv.logging import configure_logging


commands = [
    InitRosenvCommand(),
    ShellCommand(),
    InfoCommand(),
    InstallCommand(),
    RemoveCommand(),
    RosdepGenerateCommand(),
    RosdepAddCommand(),
    RosdepRemoveCommand(),
    RosdepVerifyCommand(),
    RunCommand(),
    AddCommand(),
    ClearCacheCommand(),
]


def main() -> None:
    app = Application(name=app_name, version=metadata.version("rosenv"))
    app = configure_logging(app)

    for command in commands:
        app.add(command)

    app.run()
