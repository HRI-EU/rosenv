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
from cleo.helpers import option

from robenv.commands.util import NoRosInstallationDetectedError
from robenv.commands.util import get_default_ros_path
from rosenv.commands.util import verify_existing_paths
from rosenv.environment.distro import parse_distro
from rosenv.environment.initialize import initialize
from robenv.rob.rob import ROS


_logger = getLogger(__name__)


class InitRobenvCommand(Command):
    name = "init"
    description = "Initializes the robenv at the current location"
    options = [
        option(
            "ros-path",
            description="Where is your ros-installation located? Or only for ros 2: provide a link or path to a tar.gz.",
            default=get_default_ros_path(),
            flag=False,
            value_required=True,
        ),
        option(
            "rosdep-path",
            description="Location of existing rosdep.yml file for usage of internal dependencies.",
            default=None,
            flag=False,
        ),
        option(
            "workspace-path",
            description="Location of ROS workspace, relevant for detecting internal dependencies, ie. rosdep.yml",
            default=".",
            flag=False,
        ),
    ]

    def handle(self) -> int:
        if self.option("ros-path") is None:
            raise NoRosInstallationDetectedError
        ros = ROS(str(self.option("ros-path")))

        _logger.info("Initializing robenv with ROS distribution: <fg=green>%s</>\n", ros.distro)

        rosdep_path = None
        if self.option("rosdep-path") is not None:
            rosdep_path = Path(self.option("rosdep-path"))
            verify_existing_paths(rosdep_path)

        workspace_path = Path(self.option("workspace-path"))
        verify_existing_paths(workspace_path)

        robenv = initialize(
            ros_path=ros.path,
            ros_distro=ros.distro,
            rosdep_path=rosdep_path,
            workspace_path=workspace_path,
        )
        _logger.info("Linking files:\tsuccess")

        robenv.rosdep.init()
        _logger.info("rosdep init:\tsuccess")
        robenv.rosdep.update(ros.distro)
        _logger.info("rosdep update:\tsuccess")

        return 0
