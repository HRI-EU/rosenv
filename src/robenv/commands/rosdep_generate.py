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

import yaml

from cleo.commands.command import Command
from cleo.helpers import argument
from cleo.helpers import option
from cleo.io.outputs.output import Type as OutputType

from robenv.catkin_profile.profile import CatkinProfile
from robenv.commands.util import NoRosInstallationDetectedError
from robenv.commands.util import get_default_ros_path
from robenv.environment.distro import parse_distro
from robenv.ros_package.workspace import ROSWorkspace
from robenv.rosdep.rosdep import Rosdep


class RosdepGenerateCommand(Command):
    name = "rosdep generate"
    description = "Generate rosdep.yaml based on your workspace."
    arguments = [
        argument(
            "workspace",
            description="Where is the workspace we want to discover?",
            optional=True,
            multiple=False,
            default=".",
        ),
    ]
    options = [
        option(
            "ros-path",
            description="Where is your ros-installation located?",
            default=get_default_ros_path(),
            flag=False,
            value_required=True,
        ),
        option(
            "output",
            description="Write content directly into the specified file",
            flag=False,
            multiple=False,
        ),
    ]

    @property
    def _workspace_path(self) -> Path:
        return Path(self.argument("workspace"))

    def handle(self) -> int:
        if self.option("ros-path") is None:
            raise NoRosInstallationDetectedError

        ros_distro = parse_distro(Path(self.option("ros-path")).name)
        workspace = ROSWorkspace.from_workspace(
            self._workspace_path,
            CatkinProfile.with_no_blacklist(),
        )

        dump = yaml.dump(
            Rosdep.generate_rosdep_from_workspace(
                workspace,
                ros_distro,
            ),
        )

        if (output := self.option("output")) is not None:
            Path(output).write_text(dump)
        else:
            self.io.write(dump, type=OutputType.PLAIN)

        return 0
