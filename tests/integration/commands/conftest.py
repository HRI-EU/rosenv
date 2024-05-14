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

import shutil

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from pytest_mock import MockerFixture

from tests.integration.commands import package_name


@pytest.fixture()
def deb_name() -> str:
    return f"ros-noetic-{package_name()}_0.0.0-0focal_amd64.deb"


@pytest.fixture()
def url(deb_name: str) -> str:
    return f"https://domain.tld/{deb_name}"


@pytest.fixture()
def apt_get_download_print_uris_line(url: str, deb_name: str) -> str:
    return f"'{url}' {deb_name} 161276 SHA512:d2f588c0bcd2f588c0bcd2f588c0bc0bc"


@pytest.fixture()
def build_artifact(dist_path: Path, test_debs: Path, deb_name: str) -> Path:
    deb_file = test_debs / deb_name

    assert deb_file.exists()

    dist_path.mkdir(exist_ok=True)

    temp_deb_file = dist_path / deb_name
    assert not temp_deb_file.exists()
    shutil.copy(deb_file, temp_deb_file)

    assert temp_deb_file.exists()

    return temp_deb_file


@pytest.fixture()
def nodeps(test_debs: Path) -> Path:
    return test_debs / "nodeps_0.0.0_all.deb"


@pytest.fixture()
def dep_on_nodeps(test_debs: Path) -> Path:
    return test_debs / "dep-on-nodeps_0.0.0_all.deb"


@pytest.fixture(autouse=True)
def requests_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("robenv.commands.add.requests")


@pytest.fixture(autouse=True)
def run_command_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("robenv.commands.add.run_command")
