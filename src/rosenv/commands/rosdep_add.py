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

from cleo.commands.command import Command
from cleo.helpers import argument
from cleo.helpers import option

from rosenv.environment.env import RosEnv
from rosenv.ros_package.package import PackageName
from rosenv.rosdep.rosdep import ResolvedPackageName
from rosenv.rosdep.rosdep import Rosdep
from rosenv.rosdep.rosdep import SystemName


_logger = getLogger(__name__)


class RosdepAddCommand(Command):
    name = "rosdep add"
    description = "Add dependency mapping to rosdep yaml"
    arguments = [
        argument(
            "dependency",
            description="The name of the rosdep dependency, what is the name of the package in the package.xml",
        ),
        argument(
            "translation",
            description="The translation of the rosdep dependency for your chosen system dependency",
        ),
    ]
    options = [
        option(
            "workspace",
            flag=False,
            description="Where is the workspace we want to discover?",
            default=".",
        ),
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
        option(
            "system",
            description="Specify for which system you are translating, default is autodetection",
            flag=False,
            default=Rosdep.get_rosdep_system(),
        ),
        option(
            "pip-dependency",
            description="If your translated dependency should be a pip-dependency, "
            "otherwise it will be the detected system installer",
            flag=True,
        ),
    ]

    @property
    def _workspace_path(self) -> Path:
        return Path(self.option("workspace"))

    @property
    def _overwrite(self) -> bool:
        return not self.option("no-overwrite")

    def handle(self) -> int:
        rosdep = RosEnv().rosdep

        system = SystemName(self.option("system"))
        dependency = PackageName(self.argument("dependency"))
        translation = ResolvedPackageName(self.argument("translation"))

        if self.option("pip-dependency"):
            rosdep.add_pip(system, dependency, translation)
        else:
            rosdep.add(system, dependency, translation)

        if self._overwrite:
            _logger.info("Added dependency to rosdep structure")

            rosdep.save()

            if self.option("run-update"):
                _logger.info("Running 'rosdep update'...")
                rosdep.update()
                _logger.info("'rosdep update'...success!")
        else:
            rosdep.print_to_stdout()

        return 0
