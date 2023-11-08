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

import sys

from pathlib import Path
from string import Template

import rosenv.templates

from rosenv.environment.distro import RosDistribution
from rosenv.environment.distro import get_distro_config


if sys.version_info < (3, 9):
    from importlib_resources import files
else:
    from importlib.resources import files


def get_activate_contents(
    rosenv_path: Path,
    rosenv_ros_path: Path,
    rosdep_source_dir: Path,
    rosenv_cache_path: Path,
) -> str:
    activate_template = Template((files(rosenv.templates) / "activate.template").read_text())
    return activate_template.substitute(
        {
            "rosenv_ros_path": str(rosenv_ros_path.absolute()),
            "rosdep_source_dir": str(rosdep_source_dir.absolute()),
            "rosenv_name": str(rosenv_path.absolute().parent.name),
            "rosenv_cache_path": str(rosenv_cache_path.absolute()),
            "rosenv_path": str(rosenv_path.absolute()),
        },
    )


def get_local_setup_contents(rosenv_ros_path: Path) -> str:
    local_setup_template = Template((files(rosenv.templates) / "local_setup.sh.template").read_text())
    return local_setup_template.substitute(
        {
            "ros_folder": str(rosenv_ros_path.absolute()),
        },
    )


def get_setup_contents(rosenv_ros_path: Path, activate_file: Path, distribution: RosDistribution) -> str:
    setup_template = Template((files(rosenv.templates) / "setup.sh.template").read_text())
    return setup_template.substitute(
        {
            "ros_folder": str(rosenv_ros_path.absolute()),
            "activate_file": str(activate_file.absolute()),
            "variable_name": get_distro_config(distribution).builder_tool_variable_name,
            "distribution": distribution,
        },
    )
