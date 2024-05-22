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

import os
import shutil

from pathlib import Path

import pytest

from cleo.application import Application
from cleo.commands.command import Command
from cleo.testers.command_tester import CommandTester

from robenv.cli import commands
from tests.conftest import YieldFixture


@pytest.fixture(autouse=True)
def change_cwd(robenv_target_path: Path) -> YieldFixture[Path]:
    original_cwd = Path.cwd()
    os.chdir(robenv_target_path.parent)

    yield robenv_target_path.parent

    os.chdir(original_cwd)


@pytest.fixture()
def app() -> Application:
    application = Application()

    for command in commands:
        assert isinstance(command, Command)

        application.add(command)

    return application


@pytest.fixture()
def init_app(
    change_cwd: Path,  # noqa: ARG001
    app: Application,
) -> Application:
    CommandTester(app.find("init")).execute()

    return app


@pytest.fixture()
def robenv_target_path(tmp_path: Path) -> Path:
    robenv_target = tmp_path / "robenv"
    assert not robenv_target.exists()
    return robenv_target


@pytest.fixture()
def ros_workspace_path(tmp_path: Path) -> Path:
    ros_workspace_path = tmp_path / "src"
    ros_workspace_path.mkdir(exist_ok=True)

    return ros_workspace_path


@pytest.fixture()
def dist_path(tmp_path: Path) -> Path:
    dist_path = tmp_path / "dist"
    dist_path.mkdir(exist_ok=True)
    return dist_path


@pytest.fixture()
def _copy_minimal_example_project(robenv_target_path: Path, example_project: Path) -> YieldFixture[None]:
    target_folder = robenv_target_path.parent / "src"
    target_folder.mkdir(exist_ok=True, parents=True)

    adder_project = example_project / "src" / "adder"

    assert adder_project.exists(), "Adder project doesn't exist, cannot copy minimal example"

    shutil.copytree(adder_project, target_folder / "adder")

    yield

    # cleanup for space
    shutil.rmtree(target_folder, ignore_errors=True)


@pytest.fixture()
def _copy_full_example_project(robenv_target_path: Path, example_project: Path) -> YieldFixture[None]:
    target_folder = robenv_target_path.parent / "src"

    # copy only "src" so we filter out probably unwanted things (like robenv, etc)
    entire_example_project = example_project / "src"

    assert entire_example_project.exists(), "Adder project doesn't exist, cannot copy minimal example"

    shutil.copytree(entire_example_project, target_folder)

    yield

    # cleanup for space
    shutil.rmtree(target_folder, ignore_errors=True)
