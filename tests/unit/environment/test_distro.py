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

from rosenv.environment.distro import UnknownRosDistributionError
from rosenv.environment.distro import get_installed_distro_paths
from rosenv.environment.distro import is_eol_distro
from rosenv.environment.distro import parse_distro


def test_parse_distro_should_return_known_distro_unchanged() -> None:
    assert parse_distro("noetic") == "noetic"
    assert parse_distro("galactic") == "galactic"
    assert parse_distro("foxy") == "foxy"


def test_parse_distro_should_raise_when_distro_is_unknown() -> None:
    with pytest.raises(UnknownRosDistributionError):
        parse_distro("unknown")


def test_distro_should_report_when_distro_is_eol() -> None:
    assert is_eol_distro("melodic")
    assert is_eol_distro("foxy")
    assert is_eol_distro("galactic")

    assert not is_eol_distro("noetic")
    assert not is_eol_distro("iron")


def test_distro_should_report_existing_distros(tmp_path: Path) -> None:
    (tmp_path / "noetic").mkdir()
    (tmp_path / "foxy").mkdir()
    (tmp_path / "galactic").mkdir()

    installed_distro_count = 3

    installed = get_installed_distro_paths(base_ros_path=tmp_path)

    assert len(installed) == installed_distro_count

    assert tmp_path / "noetic" in installed
    assert tmp_path / "foxy" in installed
    assert tmp_path / "galactic" in installed
