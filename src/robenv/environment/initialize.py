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
from contextlib import suppress
from dataclasses import dataclass
from logging import getLogger
from pathlib import Path

from deb_pkg_tools.package import shutil

from robenv.environment.distro import RosDistribution
from robenv.environment.distro import get_distro_config
from robenv.environment.env import DEFAULT_ROBENV_NAME
from robenv.environment.env import RobEnv
from robenv.environment.env import RobEnvSettings
from robenv.environment.locate import RobEnvNotFoundError
from robenv.rosdep.initialize import initialize_rosdep
from robenv.rosdep.rosdep import get_sources_list
from robenv.templates import get_activate_contents
from robenv.templates import get_local_setup_contents
from robenv.templates import get_setup_contents


_logger = getLogger(__name__)


@dataclass()
class RobEnvInitConfig:
    robenv_path: Path
    workspace_path: Path
    ros_path: Path
    ros_distro: RosDistribution
    rosdep_path: Path | None

    @property
    def robenv_ros_path(self) -> Path:
        return self.robenv_path / "opt/ros" / self.ros_distro

    @property
    def robenv_cache_path(self) -> Path:
        return self.robenv_path / "cache"


class RobEnvExistsError(Exception):
    def __init__(self, robenv_path: Path) -> None:
        super().__init__(
            f"robenv at {robenv_path} already exists\n"
            f"Solutions: continue with existing robenv installation, "
            f"or delete {robenv_path.absolute()} then initialize again.",
        )


def _copy_ros_files(
    src: Path,
    dest: Path,
    distribution: RosDistribution,
) -> None:
    for setup_name in get_distro_config(distribution).files_to_copy:
        if (src / setup_name).exists():
            _logger.debug(
                "copying: %s -> %s",
                str(src / setup_name),
                str(dest / setup_name),
            )
            shutil.copy(
                src / setup_name,
                dest / setup_name,
            )
        else:
            _logger.debug(
                "file not exists: %s -> %s",
                str(src / setup_name),
                str(dest / setup_name),
            )


def _symlink_ros_files(
    robenv_path: Path,
    config: RobEnvInitConfig,
) -> None:
    distro_config = get_distro_config(config.ros_distro)

    for setup_name in distro_config.files_to_link:
        ros_file = config.ros_path / setup_name
        _logger.debug("creating symlink: %s -> %s", robenv_path / setup_name, ros_file)
        if ros_file.exists():
            (robenv_path / setup_name).symlink_to(
                ros_file,
                target_is_directory=False,
            )


def _create_new_files(config: RobEnvInitConfig) -> None:
    ros_dir = config.robenv_ros_path

    initialize_rosdep(config.robenv_path, config.workspace_path, config.ros_distro, config.rosdep_path)

    activate_file = (config.robenv_path / "activate").absolute()
    activate_file.write_text(
        get_activate_contents(
            robenv_path=config.robenv_path,
            robenv_ros_path=config.robenv_ros_path,
            rosdep_source_dir=get_sources_list(config.robenv_path).parent,
            robenv_cache_path=config.robenv_cache_path,
        ),
    )

    distro_config = get_distro_config(config.ros_distro)
    if "local_setup.sh" not in distro_config.files_to_copy:
        (ros_dir / "local_setup.sh").write_text(get_local_setup_contents(config.robenv_ros_path))

    (ros_dir / "setup.sh").write_text(
        get_setup_contents(
            config.robenv_ros_path,
            activate_file,
            config.ros_distro,
        ),
    )

    RobEnvSettings.initialize(config.robenv_path, config.ros_distro)


def initialize(
    ros_path: Path,
    ros_distro: RosDistribution,
    rosdep_path: Path | None,
    workspace_path: Path,
) -> RobEnv:
    with suppress(RobEnvNotFoundError):
        dummy_robenv = RobEnv()
        raise RobEnvExistsError(dummy_robenv.path)

    config = RobEnvInitConfig(
        robenv_path=Path(DEFAULT_ROBENV_NAME),
        ros_distro=ros_distro,
        workspace_path=workspace_path,
        ros_path=ros_path,
        rosdep_path=rosdep_path,
    )

    robenv_ros_path = config.robenv_ros_path
    robenv_ros_path.mkdir(parents=True, exist_ok=True)

    _copy_ros_files(config.ros_path, robenv_ros_path, config.ros_distro)
    _symlink_ros_files(robenv_ros_path, config)
    _create_new_files(config)

    return RobEnv()
