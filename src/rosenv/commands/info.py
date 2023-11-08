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

from rosenv.commands.util import get_workspace
from rosenv.environment.env import RosEnv
from rosenv.ros_package.package import PackageName


_logger = getLogger(__name__)


class InfoCommand(Command):
    name = "info"
    description = "Get detailed info about your workspace or package"
    arguments = [
        argument(
            "workspace_or_packagename",
            description="About which workspace path or package name did you want more informations?",
            multiple=False,
            optional=True,
        ),
    ]
    options = [
        option(
            "catkin-folder",
            flag=False,
            description="Where can we find the .catkin_tools folder? By default we look on the same level as rosenv",
        ),
        option(
            "catkin-profile",
            short_name="p",
            flag=False,
            description="Which profile if any should we use for blacklists",
        ),
    ]

    @staticmethod
    def _package_info(package_name: PackageName, rosenv: RosEnv) -> None:
        deb_path = rosenv.get_package_deb_path(package_name)

        _logger.info("package Name: %s", package_name)
        _logger.info("package Path: %s \n", deb_path)
        deb_info = rosenv.shell.run(f"dpkg-deb -I {deb_path}", Path.cwd())

        for line in deb_info.splitlines():
            if any(x in line for x in ("Version", "Package", "Architecture", "Maintainer")):
                _logger.info(line.strip())

    @staticmethod
    def _env_info(rosenv: RosEnv) -> None:
        _logger.info("packages installed in env: %s", rosenv.get_installed_packages())

    def _workspace_info(self, workspace_path: Path, rosenv: RosEnv) -> None:
        workspace = get_workspace(workspace_path, rosenv, self.option("catkin-folder"), self.option("catkin-profile"))

        _logger.info("project_package_count: %s", len(workspace.ros_packages))
        _logger.info("build_order: %s", [p.name for p in workspace.sort_ros_packages_for_installation()])
        _logger.info("external dependencies: %s", [p.name for p in workspace.external_dependencies])

        stagestr = ""

        for index, stage in enumerate(workspace.get_install_tree()):
            stagestr += f"\tStage {index + 1}:\n"
            for package in stage:
                stagestr += f"\t\t- {package.name}\n"

        _logger.info("build stages: \n%s", stagestr)

    def handle(self) -> int:
        workspace_or_packagename = self.argument("workspace_or_packagename")

        workspace_path = Path(workspace_or_packagename).resolve()
        rosenv = RosEnv()

        self._env_info(rosenv)
        package_name = PackageName(workspace_or_packagename)
        if rosenv.is_installed(package_name):
            self._package_info(workspace_or_packagename, rosenv)

        if workspace_path.exists():
            self._workspace_info(workspace_path, rosenv)

        return 0
