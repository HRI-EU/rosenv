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

from concurrent.futures import as_completed
from logging import getLogger
from pathlib import Path

from cleo.commands.command import Command
from cleo.helpers import option

from robenv.catkin_profile import CatkinProfile
from robenv.environment.env import RobEnv
from robenv.ros_package.package import ExternalDependency
from robenv.ros_package.package import PackageName
from robenv.ros_package.package import ROSPackage
from robenv.ros_package.workspace import ROSWorkspace
from robenv.util.cancelable_executor import CancelableExecutor
from robenv.util.cpu_count import get_cpu_count


_logger = getLogger(__name__)


class RosdepVerifyCommand(Command):
    name = "rosdep verify"
    description = "Verify that all relevant dependencies can be resolved correctly"
    options = [
        option(
            "workspace",
            flag=False,
            description="Where is the workspace we want to discover?",
            default=".",
        ),
    ]

    @staticmethod
    def _to_tuple(package: ROSPackage | ExternalDependency) -> tuple[PackageName, list[PackageName]]:
        if isinstance(package, ExternalDependency):
            return package.name, [p.name for p in package.required_by]

        return package.name, []

    @staticmethod
    def _check_dependencies(
        given_dependencies: list[ROSPackage] | list[ExternalDependency],
        robenv: RobEnv,
    ) -> list[tuple[PackageName, list[PackageName]]]:
        with CancelableExecutor(max_workers=get_cpu_count(minimum=4)) as pool:
            futures = {
                pool.submit(robenv.rosdep.resolve, dependency.name): dependency for dependency in given_dependencies
            }

            return [
                RosdepVerifyCommand._to_tuple(futures[future])
                for future in as_completed(futures)
                if future.exception() is not None
            ]

    @staticmethod
    def _translate_required_by(required_by: list[PackageName]) -> str:
        if len(required_by) == 0:
            return "for itself"

        return f"required by {required_by}"

    @staticmethod
    def _to_string(failed_dependencies: list[tuple[PackageName, list[PackageName]]]) -> str:
        return "\n".join(
            (
                f"\t- {failed_dependency[0]} {RosdepVerifyCommand._translate_required_by(failed_dependency[1])}"
                for failed_dependency in failed_dependencies
            ),
        )

    def handle(self) -> int:
        robenv = RobEnv()

        workspace = ROSWorkspace.from_workspace(
            Path(self.option("workspace")).resolve(),
            CatkinProfile.with_no_blacklist(),
        )

        internal_packages = workspace.sort_ros_packages_for_installation()
        external_packages = workspace.external_dependencies

        failed_internals = self._check_dependencies(internal_packages, robenv)
        failed_externals = self._check_dependencies(external_packages, robenv)
        failed_dependencies = failed_internals + failed_externals

        if len(failed_dependencies) == 0:
            _logger.info("All dependencies found!")
            return 0

        _logger.warning(
            """\
Cannot find following dependencies:
%s

Please fix the rosdep.yaml at: %s
Then run `rosdep update` inside a `robenv shell`!
""",
            RosdepVerifyCommand._to_string(failed_dependencies),
            str(robenv.rosdep.get_rosdep_yml_file_path()),
        )
        return 1
