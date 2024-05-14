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

from robenv.commands.util import PathDoesNotExistError
from robenv.commands.util import get_catkin_tools_folder
from robenv.commands.util import get_optional_profile
from robenv.commands.util import verify_existing_paths
from robenv.util.paths import remove_slash_prefix


def test_get_optional_profile_should_give_empty_profile_when_no_name_given(tmp_path: Path) -> None:
    profile = get_optional_profile(catkin_tools_folder=tmp_path, profile_name=None)

    assert profile.blacklist == []


def test_get_optional_profile_should_get_real_profile_if_existing(
    catkin_tools: Path,
) -> None:
    profile = get_optional_profile(
        catkin_tools_folder=catkin_tools,
        profile_name="default",
    )

    assert profile.blacklist == ["adder", "adder_srvs"]


def test_verify_existing_paths_does_not_raise_if_everything_exists(tmp_path: Path) -> None:
    file_list = [tmp_path / f for f in ("a", "b", "c", "d")]

    for f in file_list:
        f.touch()

    try:
        verify_existing_paths(*file_list)
    except Exception as e:  # noqa: BLE001
        pytest.fail(f"No exception expected but got: {e}")


def test_verify_existing_paths_finds_non_existing_paths(tmp_path: Path) -> None:
    file_list = [tmp_path / f for f in ("a", "b", "c", "d")]

    for f in file_list[:-1]:
        f.touch()

    with pytest.raises(PathDoesNotExistError) as error:
        verify_existing_paths(*file_list)

    assert error.value.path == file_list[-1]


def test_get_catkin_folder_should_get_folder_on_the_same_level_as_robenv() -> None:
    robenv_path = Path()

    assert get_catkin_tools_folder(robenv_path) == (robenv_path.parent / ".catkin_tools").absolute()


def test_get_catkin_folder_should_get_overwritten_by_argument() -> None:
    robenv_path = Path()
    catkin_folder = "test_catkin_folder"

    assert (
        get_catkin_tools_folder(
            robenv_path,
            catkin_folder,
        )
        == Path("test_catkin_folder").absolute()
    )


def test_get_catkin_folder_should_return_absolute_paths() -> None:
    robenv_path = Path()
    assert get_catkin_tools_folder(robenv_path).is_absolute()

    catkin_folder = "test_catkin_folder"
    assert get_catkin_tools_folder(robenv_path, catkin_folder).is_absolute()


def test_remove_slash_prefix() -> None:
    assert remove_slash_prefix(Path("/opt/ros/noetic")) == Path("opt/ros/noetic")
    assert remove_slash_prefix(Path("opt/ros/noetic")) == Path("opt/ros/noetic")
    assert remove_slash_prefix("/opt/ros/noetic") == Path("opt/ros/noetic")
    assert remove_slash_prefix("opt/ros/noetic") == Path("opt/ros/noetic")
    assert remove_slash_prefix("/") == Path("")  # noqa: PTH201
    assert remove_slash_prefix("") == Path("")  # noqa: PTH201
    assert isinstance(remove_slash_prefix(Path("opt/ros/noetic")), Path)
    assert isinstance(remove_slash_prefix("opt/ros/noetic"), Path)
