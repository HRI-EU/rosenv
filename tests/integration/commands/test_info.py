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

import pytest

from cleo.application import Application
from cleo.testers.command_tester import CommandTester
from pytest_mock import MockerFixture

from rosenv.commands.info import InfoCommand
from rosenv.environment.distro import RosDistribution
from tests.integration.commands import assert_adder_is_installed


@pytest.fixture()
def package_info_spy(mocker: MockerFixture) -> MagicMock:
    return mocker.spy(InfoCommand, "_package_info")


@pytest.fixture()
def env_info_spy(mocker: MockerFixture) -> MagicMock:
    return mocker.spy(InfoCommand, "_env_info")


@pytest.fixture()
def workspace_info_spy(mocker: MockerFixture) -> MagicMock:
    return mocker.spy(InfoCommand, "_workspace_info")


@pytest.mark.usefixtures("_copy_minimal_example_project")
def test_info_package(
    deb_name: str,
    build_artifact: Path,
    init_app: Application,
    rosenv_target_path: Path,
    package_info_spy: MagicMock,
    env_info_spy: MagicMock,
    workspace_info_spy: MagicMock,
    ros_distro: RosDistribution,
) -> None:
    CommandTester(init_app.find("add")).execute(f"adder {build_artifact}")
    assert_adder_is_installed(rosenv_target_path, deb_name, ros_distro)

    assert not package_info_spy.called
    assert not env_info_spy.called
    assert not workspace_info_spy.called

    CommandTester(init_app.find("info")).execute("adder")

    assert package_info_spy.called
    assert env_info_spy.called
    assert not workspace_info_spy.called


@pytest.mark.usefixtures("_copy_minimal_example_project")
def test_info_workspace(
    deb_name: str,
    build_artifact: Path,
    init_app: Application,
    rosenv_target_path: Path,
    package_info_spy: MagicMock,
    env_info_spy: MagicMock,
    workspace_info_spy: MagicMock,
    ros_distro: RosDistribution,
) -> None:
    CommandTester(init_app.find("add")).execute(f"adder {build_artifact}")
    assert_adder_is_installed(rosenv_target_path, deb_name, ros_distro)

    assert not package_info_spy.called
    assert not env_info_spy.called
    assert not workspace_info_spy.called

    CommandTester(init_app.find("info")).execute("src")

    assert not package_info_spy.called
    assert env_info_spy.called
    assert workspace_info_spy.called
