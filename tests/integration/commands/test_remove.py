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

import pytest

from cleo.application import Application
from cleo.testers.command_tester import CommandTester

from robenv.environment.distro import RosDistribution
from robenv.environment.env import PackageIsNotInstalledError
from robenv.environment.env import RemoveDependencyError
from tests.integration.commands import assert_is_installed
from tests.integration.commands import assert_is_not_installed


def test_remove_package(
    init_app: Application,
    robenv_target_path: Path,
    ros_distro: RosDistribution,
    nodeps: Path,
) -> None:
    CommandTester(init_app.find("add")).execute(f"{nodeps}")

    assert_is_installed(robenv_target_path, nodeps.name, ros_distro)

    CommandTester(init_app.find("remove")).execute("nodeps")

    assert_is_not_installed(robenv_target_path, nodeps.name, ros_distro)


def test_remove_package_but_not_installed(
    init_app: Application,
    robenv_target_path: Path,
    ros_distro: RosDistribution,
    nodeps: Path,
) -> None:
    assert_is_not_installed(robenv_target_path, nodeps.name, ros_distro)

    with pytest.raises(PackageIsNotInstalledError):
        CommandTester(init_app.find("remove")).execute("nodeps")


def test_remove_package_with_dependents(
    init_app: Application,
    robenv_target_path: Path,
    ros_distro: RosDistribution,
    nodeps: Path,
    dep_on_nodeps: Path,
) -> None:
    CommandTester(init_app.find("add")).execute(f"{nodeps!s}")
    assert_is_installed(robenv_target_path, nodeps.name, ros_distro)
    CommandTester(init_app.find("add")).execute(f"{dep_on_nodeps!s}")
    assert_is_installed(robenv_target_path, dep_on_nodeps.name, ros_distro)

    with pytest.raises(RemoveDependencyError):
        CommandTester(init_app.find("remove")).execute("nodeps")

    assert_is_installed(robenv_target_path, nodeps.name, ros_distro)

    CommandTester(init_app.find("remove")).execute("nodeps --force")

    assert_is_not_installed(robenv_target_path, nodeps.name, ros_distro)
