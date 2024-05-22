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

from robenv.commands.util import get_workspace
from robenv.environment.env import RobEnv
from robenv.ros_package.builder import Builder
from robenv.ros_package.checker import Checker
from robenv.util.cpu_count import get_cpu_count


_logger = getLogger(__name__)


class InstallCommand(Command):
    name = "install"
    aliases = ["build"]
    description = "Build a workspace or package and install the result into the robenv"
    arguments = [
        argument(
            "workspace",
            description="Where is the workspace we want to discover?",
            multiple=False,
        ),
    ]
    options = [
        option(
            "no-overwrite",
            description="Don't overwrite existing deb-files",
        ),
        option(
            "can-fail",
            description="Don't abort if a package fails to build",
        ),
        option(
            "no-check-launchfiles",
            description="Don't check for missing launch files",
        ),
        option(
            "check-launchfiles-will-fail",
            description="Unsuccessful checks will cause the build to fail.",
        ),
        option(
            "dist-folder",
            short_name="o",
            flag=False,
            description="Where to put all the deb-files after building",
            default="dist",
        ),
        option(
            "catkin-folder",
            flag=False,
            description="Where can we find the .catkin_tools folder? By default we look on the same level as robenv",
        ),
        option(
            "catkin-profile",
            short_name="p",
            flag=False,
            description="Which profile if any should we use for blacklists",
        ),
        option(
            "jobs",
            short_name="j",
            flag=False,
            description="How many projects can we build concurrently at maximum? "
            "0 or below means that we use your core-count",
            value_required=False,
        ),
    ]

    @property
    def _overwrite(self) -> bool:
        return not self.option("no-overwrite")

    @property
    def _can_fail(self) -> bool:
        return bool(self.option("can-fail"))

    @property
    def check(self) -> bool:
        return not self.option("no-check-launchfiles")

    @property
    def _check_will_fail(self) -> bool:
        return bool(self.option("check-launchfiles-will-fail"))

    @property
    def _jobs(self) -> int:
        jobs = self.option("jobs")

        if jobs is None:
            return 1

        if (job_count := int(jobs)) <= 0:
            return get_cpu_count(minimum=2)

        return job_count

    def handle(self) -> int:
        dist_folder = Path(self.option("dist-folder"))
        dist_folder.mkdir(exist_ok=True, parents=True)

        robenv = RobEnv()

        workspace_path = Path(self.argument("workspace")).resolve()
        workspace = get_workspace(workspace_path, robenv, self.option("catkin-folder"), self.option("catkin-profile"))

        builder = Builder(
            robenv,
            dist_folder,
            overwrite=self._overwrite,
            max_workers=self._jobs,
            checker=Checker(check=self.check, check_will_fail=self._check_will_fail),
            can_fail=self._can_fail,
        )

        if self._jobs != 1:
            _logger.info("Building with maximum of %s jobs", self._jobs)

        build_result = builder.build_workspace(workspace)

        if any(build_result.failed_packages):
            _logger.error("Failed Packages:")
            for package_name in build_result.failed_packages:
                _logger.error("\t%s", package_name)

        if any(build_result.missing_launch_files):
            _logger.error("Missing launch files:")
            for missing_launch_files in filter(bool, build_result.missing_launch_files):
                _logger.error("\t%s:", str(missing_launch_files.package.name))
                for file in missing_launch_files.missing_files:
                    _logger.error("\t\t- %s", str(file.relative_to(missing_launch_files.package.path)))

        return 0
