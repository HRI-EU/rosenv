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

import robenv.templates

from robenv.environment.distro import RosDistribution
from robenv.environment.distro import get_distro_config


if sys.version_info < (3, 9):
    from importlib_resources import files
else:
    from importlib.resources import files


def get_activate_contents(
    robenv_path: Path,
    robenv_ros_path: Path,
    rosdep_source_dir: Path,
    robenv_cache_path: Path,
) -> str:
    activate_template = Template((files(robenv.templates) / "activate.template").read_text())
    return activate_template.substitute(
        {
            "robenv_ros_path": str(robenv_ros_path.absolute()),
            "rosdep_source_dir": str(rosdep_source_dir.absolute()),
            "robenv_name": str(robenv_path.absolute().parent.name),
            "robenv_cache_path": str(robenv_cache_path.absolute()),
            "robenv_path": str(robenv_path.absolute()),
        },
    )


def get_local_setup_contents(robenv_ros_path: Path) -> str:
    local_setup_template = Template((files(robenv.templates) / "local_setup.sh.template").read_text())
    return local_setup_template.substitute(
        {
            "ros_folder": str(robenv_ros_path.absolute()),
        },
    )


def get_setup_contents(robenv_ros_path: Path, activate_file: Path, distribution: RosDistribution) -> str:
    setup_template = Template((files(robenv.templates) / "setup.sh.template").read_text())
    return setup_template.substitute(
        {
            "ros_folder": str(robenv_ros_path.absolute()),
            "activate_file": str(activate_file.absolute()),
            "variable_name": get_distro_config(distribution).builder_tool_variable_name,
            "distribution": distribution,
        },
    )
