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

from collections.abc import Iterator
from pathlib import Path

import pytest

from robenv.environment.env import DEFAULT_ROBENV_NAME
from robenv.environment.locate import RobEnvNotFoundError
from robenv.environment.locate import locate


@pytest.fixture()
def candidate_dir(resources: Path) -> Path:
    candidate_dir = resources / "locate_robenv_tree"
    assert candidate_dir.exists()
    return candidate_dir


# git does not allow commiting a dir with name ".git", so it must be created at runtime
@pytest.fixture()
def _make_git_dir(candidate_dir: Path) -> Iterator[None]:
    git_dir = candidate_dir / "with_git" / ".git"
    git_dir.mkdir()
    yield
    git_dir.rmdir()


@pytest.mark.usefixtures("_make_git_dir")
def test_stops_at_git_root(candidate_dir: Path) -> None:
    cwd = candidate_dir / "with_git/dir"
    assert cwd.exists()

    with pytest.raises(RobEnvNotFoundError):
        locate(DEFAULT_ROBENV_NAME, path=cwd)


def test_stops_at_pyproject_toml(candidate_dir: Path) -> None:
    cwd = candidate_dir / "with_pyproject_toml/dir"
    assert cwd.exists()

    with pytest.raises(RobEnvNotFoundError):
        locate(DEFAULT_ROBENV_NAME, path=cwd)


def test_stops_at_root_dir() -> None:
    cwd = Path("/foo")

    with pytest.raises(RobEnvNotFoundError):
        locate(DEFAULT_ROBENV_NAME, path=cwd)


def test_finds_robenv(candidate_dir: Path) -> None:
    cwd = candidate_dir / "with_git_submodule/dir"
    assert cwd.exists()

    robenv_path = locate(DEFAULT_ROBENV_NAME, path=cwd)

    assert robenv_path == candidate_dir / "robenv"


def test_does_not_stop_at_git_submodule(candidate_dir: Path) -> None:
    cwd = candidate_dir / "with_git_submodule/dir"
    assert cwd.exists()

    robenv_path = locate(DEFAULT_ROBENV_NAME, path=cwd)

    assert robenv_path is not None
    assert not (robenv_path / ".git").is_file()
