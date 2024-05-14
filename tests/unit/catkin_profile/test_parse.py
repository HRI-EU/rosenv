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

from robenv.catkin_profile import CatkinProfileNotFoundError
from robenv.catkin_profile import get_profile
from robenv.catkin_profile import parse_profiles


def test_parse_profiles_should_get_all_profiles(catkin_tools: Path) -> None:
    profiles = parse_profiles(catkin_tools)

    assert profiles["default"].blacklist == ["adder", "adder_srvs"]
    assert profiles["alternative"].blacklist == ["adder"]


def test_get_profile_should_find_blacklist(catkin_tools: Path) -> None:
    profile = get_profile(catkin_tools, "default")

    assert profile.blacklist == ["adder", "adder_srvs"]


def test_get_profile_should_raise_on_unknown_profile(catkin_tools: Path) -> None:
    with pytest.raises(CatkinProfileNotFoundError) as e:
        get_profile(catkin_tools, "unknown_profile")

    e.match(r"^.*unknown_profile.*not found!$")


def test_get_profile_should_raise_if_folder_not_exists(tmp_path: Path) -> None:
    with pytest.raises(CatkinProfileNotFoundError) as e:
        get_profile(tmp_path, "irrelevant")

    e.match(r"^No Catkin profiles found!$")
