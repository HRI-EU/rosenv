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

from robenv.commands.add import AddCommand
from robenv.commands.add import NoDownloadUrlError
from robenv.environment.distro import RosDistribution
from robenv.environment.env import FileAlreadyInstalledError
from robenv.environment.env import UnmetDependencyError
from robenv.environment.run_command import CommandAbortedError
from robenv.environment.run_command import CommandFailedError
from tests.integration.commands import MockResponse
from tests.integration.commands import assert_is_installed
from tests.integration.commands import assert_is_not_installed


@pytest.fixture()
def download_spy(mocker: MockerFixture) -> MagicMock:
    return mocker.spy(AddCommand, "_download")


@pytest.fixture()
def get_apt_url_spy(mocker: MockerFixture) -> MagicMock:
    return mocker.spy(AddCommand, "_get_apt_url")


@pytest.fixture()
def download_deb_file_spy(mocker: MockerFixture) -> MagicMock:
    return mocker.spy(AddCommand, "_download_deb_file")


@pytest.fixture()
def install_nodeps(
    init_app: Application,
    nodeps: Path,
    robenv_target_path: Path,
    ros_distro: RosDistribution,
) -> Application:
    code = CommandTester(init_app.find("add")).execute(f"nodeps {nodeps!s}")
    assert code == 0
    assert_is_installed(robenv_target_path, nodeps.name, ros_distro)
    return init_app


def test_add_deb_file(
    install_nodeps: Application,
    robenv_target_path: Path,
    download_spy: MagicMock,
    get_apt_url_spy: MagicMock,
    download_deb_file_spy: MagicMock,
    ros_distro: RosDistribution,
    dep_on_nodeps: Path,
) -> None:
    assert_is_not_installed(robenv_target_path, dep_on_nodeps.name, ros_distro)

    assert not download_spy.called
    assert not get_apt_url_spy.called
    assert not download_deb_file_spy.called

    code = CommandTester(install_nodeps.find("add")).execute(f"dep-on-nodeps {dep_on_nodeps!s}")
    assert code == 0

    assert not download_spy.called
    assert not get_apt_url_spy.called
    assert not download_deb_file_spy.called

    assert_is_installed(robenv_target_path, dep_on_nodeps.name, ros_distro)


def test_add_deb_file_with_missing_dependency(
    init_app: Application,
    test_debs: Path,
    robenv_target_path: Path,
    ros_distro: RosDistribution,
) -> None:
    deb_name = "brokendeps_0.0.0_all.deb"
    assert_is_not_installed(robenv_target_path, deb_name, ros_distro)
    with pytest.raises(UnmetDependencyError):
        CommandTester(init_app.find("add")).execute(f"brokendeps {test_debs /deb_name}")
    assert_is_not_installed(robenv_target_path, deb_name, ros_distro)


def test_add_deb_file_with_missing_dependency_and_skip_check(
    init_app: Application,
    test_debs: Path,
    robenv_target_path: Path,
    ros_distro: RosDistribution,
) -> None:
    deb_name = "brokendeps_0.0.0_all.deb"
    assert_is_not_installed(robenv_target_path, deb_name, ros_distro)
    CommandTester(init_app.find("add")).execute(f"brokendeps {test_debs /deb_name} --skip-dependency-check")
    assert_is_installed(robenv_target_path, deb_name, ros_distro)


def test_add_deb_file_with_missing_alternative_dependencies(
    init_app: Application,
    test_debs: Path,
    robenv_target_path: Path,
    ros_distro: RosDistribution,
) -> None:
    deb_name = "brokenalternativesdeps_0.0.0_all.deb"
    assert_is_not_installed(robenv_target_path, deb_name, ros_distro)
    with pytest.raises(UnmetDependencyError):
        CommandTester(init_app.find("add")).execute(
            f"brokenalternativesdeps {test_debs /deb_name}",
        )
    assert_is_not_installed(robenv_target_path, deb_name, ros_distro)


def test_add_deb_file_with_available_alternative(
    install_nodeps: Application,
    test_debs: Path,
    robenv_target_path: Path,
    ros_distro: RosDistribution,
) -> None:
    deb_name = "alternativedeps_0.0.0_all.deb"
    assert_is_not_installed(robenv_target_path, deb_name, ros_distro)

    CommandTester(install_nodeps.find("add")).execute(
        f"alternativedeps {test_debs / deb_name}",
    )

    assert_is_installed(robenv_target_path, deb_name, ros_distro)


def test_add_deb_file_with_unmet_version_dependency(
    install_nodeps: Application,
    test_debs: Path,
    robenv_target_path: Path,
    ros_distro: RosDistribution,
) -> None:
    deb_name = "unmetversiondep_0.0.0_all.deb"
    assert_is_not_installed(robenv_target_path, deb_name, ros_distro)
    with pytest.raises(UnmetDependencyError):
        CommandTester(install_nodeps.find("add")).execute(
            f"unmetversiondep {test_debs /deb_name}",
        )
    assert_is_not_installed(robenv_target_path, deb_name, ros_distro)


def test_add_via_http_url(
    init_app: Application,
    robenv_target_path: Path,
    download_spy: MagicMock,
    get_apt_url_spy: MagicMock,
    download_deb_file_spy: MagicMock,
    ros_distro: RosDistribution,
    nodeps: Path,
    requests_mock: MagicMock,
) -> None:
    requests_mock.get.return_value = MockResponse(nodeps.read_bytes())
    assert_is_not_installed(robenv_target_path, nodeps.name, ros_distro)

    assert not download_spy.called
    assert not get_apt_url_spy.called
    assert not download_deb_file_spy.called

    CommandTester(init_app.find("add")).execute(f"adder https://domain.tld/{nodeps.name}")

    assert download_spy.call_count == 1
    assert not get_apt_url_spy.called
    assert download_deb_file_spy.call_count == 1

    assert_is_installed(robenv_target_path, nodeps.name, ros_distro)


def test_add_via_package_name(
    init_app: Application,
    robenv_target_path: Path,
    download_spy: MagicMock,
    get_apt_url_spy: MagicMock,
    download_deb_file_spy: MagicMock,
    ros_distro: RosDistribution,
    requests_mock: MagicMock,
    run_command_mock: MagicMock,
    nodeps: Path,
) -> None:
    requests_mock.get.return_value = MockResponse(nodeps.read_bytes())
    run_command_mock.return_value = f"https://domain.tld/{nodeps.name}"
    assert_is_not_installed(robenv_target_path, nodeps.name, ros_distro)

    assert not download_spy.called
    assert not get_apt_url_spy.called
    assert not download_deb_file_spy.called

    assert CommandTester(init_app.find("add")).execute("nodeps") == 0

    assert download_spy.call_count == 1
    assert get_apt_url_spy.call_count == 1
    assert download_deb_file_spy.call_count == 1

    assert_is_installed(robenv_target_path, nodeps.name, ros_distro)


def test_add_via_package_name_not_found(
    run_command_mock: MagicMock,
    init_app: Application,
) -> None:
    run_command_mock.return_value = ""

    with pytest.raises(NoDownloadUrlError):
        CommandTester(init_app.find("add")).execute("adder")


def test_add_deb_file_install_failed(
    run_mock: MagicMock,
    nodeps: Path,
    init_app: Application,
    robenv_target_path: Path,
    ros_distro: RosDistribution,
) -> None:
    assert not (robenv_target_path / "logs").exists()
    assert_is_not_installed(robenv_target_path, nodeps.name, ros_distro)

    run_mock.side_effect = CommandFailedError(command="command", exit_status=1, output="cool output")
    expected_return_code = 1

    assert CommandTester(init_app.find("add")).execute(f"adder {nodeps!s}") == expected_return_code

    assert (robenv_target_path / "logs" / "adder.log").exists()

    assert_is_not_installed(robenv_target_path, nodeps.name, ros_distro)


def test_add_deb_file_install_aborted(
    run_mock: MagicMock,
    init_app: Application,
    robenv_target_path: Path,
    ros_distro: RosDistribution,
    nodeps: Path,
) -> None:
    assert_is_not_installed(robenv_target_path, nodeps.name, ros_distro)

    run_mock.side_effect = CommandAbortedError(command="command", output="cool output")
    expected_return_code = 2

    assert CommandTester(init_app.find("add")).execute(f"adder {nodeps!s}") == expected_return_code

    assert_is_not_installed(robenv_target_path, nodeps.name, ros_distro)


def test_add_shows_source_package_on_file_conflict(
    init_app: Application,
    nodeps: Path,
    robenv_target_path: Path,
) -> None:
    CommandTester(init_app.find("add")).execute(
        f"adder {nodeps!s}",
    )

    with pytest.raises(FileAlreadyInstalledError) as e:
        CommandTester(init_app.find("add")).execute(
            f"adder2 {nodeps!s}",
        )
    assert e.value.installed_by_packages == ["adder"]
    assert e.value.file == robenv_target_path / "usr/share/doc/nodeps/README.Debian"


def test_add_shows_multiple_source_packages_on_file_conflict(
    init_app: Application,
    nodeps: Path,
    robenv_target_path: Path,
) -> None:
    CommandTester(init_app.find("add")).execute(
        f"adder {nodeps!s}",
    )
    CommandTester(init_app.find("add")).execute(
        f"adder2 {nodeps!s} --overwrite",
    )

    with pytest.raises(FileAlreadyInstalledError) as e:
        CommandTester(init_app.find("add")).execute(
            f"adder3 {nodeps!s}",
        )
    assert e.value.installed_by_packages == ["adder", "adder2"]
    assert e.value.file == robenv_target_path / "usr/share/doc/nodeps/README.Debian"
