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

from logging import getLogger
from pathlib import Path

import yaml

from rosenv.catkin_profile.profile import CatkinProfile
from rosenv.catkin_profile.profile import CatkinRawProfileConfig


_logger = getLogger(__name__)


class CatkinProfileNotFoundError(Exception):
    def __init__(self, catkin_profile: str | None = None) -> None:
        if catkin_profile is None:
            super().__init__("No Catkin profiles found!")
        else:
            super().__init__(f"Catkin profile with name '{catkin_profile}' not found!")


def get_profile(catkin_tools_folder: Path, catkin_profile: str) -> CatkinProfile:
    try:
        return parse_profiles(catkin_tools_folder)[catkin_profile]
    except KeyError as e:
        raise CatkinProfileNotFoundError(catkin_profile) from e


def parse_profiles(catkin_tools_folder: Path) -> dict[str, CatkinProfile]:
    result: dict[str, CatkinProfile] = {}

    profiles_folder = catkin_tools_folder / "profiles"

    if not profiles_folder.exists():
        raise CatkinProfileNotFoundError

    for profile in profiles_folder.glob("*"):
        config: CatkinRawProfileConfig = yaml.safe_load((profile / "config.yaml").read_text())

        _logger.debug("Found config for %s | %s", profile.name, config)

        result[profile.name] = CatkinProfile.from_raw(config)

    return result
