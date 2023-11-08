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

from cleo.commands.command import Command
from cleo.helpers import argument
from cleo.helpers import option

from rosenv.environment.env import RosEnv


_logger = getLogger(__name__)


class RosdepRemoveCommand(Command):
    name = "rosdep remove"
    aliases = ["rosdep rm"]
    description = "Remove dependency mapping from rosdep yaml"
    arguments = [
        argument(
            "dependency",
            description="The name of the rosdep dependency",
        ),
    ]
    options = [
        option(
            "no-overwrite",
            description="Don't overwrite file, print on stdout instead",
            flag=True,
        ),
        option(
            "run-update",
            description="Run 'rosdep update' right after adding to a file",
            flag=True,
        ),
    ]

    @property
    def _overwrite(self) -> bool:
        return not self.option("no-overwrite")

    def handle(self) -> int:
        dependency = self.argument("dependency")
        rosdep = RosEnv().rosdep
        rosdep.remove(dependency)

        if self._overwrite:
            _logger.info("Removed dependency entirely")

            rosdep.save()

            if self.option("run-update"):
                _logger.info("Running 'rosdep update'...")
                rosdep.update()
                _logger.info("'rosdep update'...success!")
        else:
            rosdep.print_to_stdout()

        return 0
