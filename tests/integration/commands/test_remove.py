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
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from cleo.application import Application
from cleo.testers.command_tester import CommandTester

from rosenv.environment.env import PackageIsNotInstalledError
from rosenv.environment.env import RemoveDependencyError
from rosenv.environment.env import RosEnv
from rosenv.ros_package.package import PackageName
from tests.conftest import YieldFixture
from tests.integration.commands import assert_adder_is_installed
from tests.integration.commands import assert_adder_is_not_installed


@pytest.fixture()
def get_dependent_packages_mock() -> YieldFixture[MagicMock]:
    with patch.object(RosEnv, "_get_dependent_packages", autospec=True) as mock:
        mock.return_value = [PackageName("server")]
        yield mock


@pytest.mark.usefixtures("_copy_minimal_example_project")
def test_remove_package(
    deb_name: str,
    build_artifact: Path,
    init_app: Application,
    rosenv_target_path: Path,
) -> None:
    CommandTester(init_app.find("add")).execute(f"adder {build_artifact}")

    assert_adder_is_installed(rosenv_target_path, deb_name)

    CommandTester(init_app.find("remove")).execute("adder")

    assert_adder_is_not_installed(rosenv_target_path, deb_name)


@pytest.mark.usefixtures("_copy_minimal_example_project")
def test_remove_package_but_not_installed(
    deb_name: str,
    init_app: Application,
    rosenv_target_path: Path,
) -> None:
    assert_adder_is_not_installed(rosenv_target_path, deb_name)

    with pytest.raises(PackageIsNotInstalledError):
        CommandTester(init_app.find("remove")).execute("adder")


@pytest.mark.usefixtures(
    "_copy_minimal_example_project",
    "get_dependent_packages_mock",
)
def test_remove_package_with_dependents(
    deb_name: str,
    build_artifact: Path,
    init_app: Application,
    rosenv_target_path: Path,
) -> None:
    CommandTester(init_app.find("add")).execute(f"adder {build_artifact}")
    assert_adder_is_installed(rosenv_target_path, deb_name)

    with pytest.raises(RemoveDependencyError):
        CommandTester(init_app.find("remove")).execute("adder")

    assert_adder_is_installed(rosenv_target_path, deb_name)

    CommandTester(init_app.find("remove")).execute("adder --force")

    assert_adder_is_not_installed(rosenv_target_path, deb_name)
