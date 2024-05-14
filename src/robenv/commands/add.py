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
from tempfile import TemporaryDirectory

import requests

from cleo.commands.command import Command
from cleo.helpers import argument
from cleo.helpers import option
from deb_pkg_tools.package import parse_filename

from robenv.environment.env import DebName
from robenv.environment.env import Installable
from robenv.environment.env import RobEnv
from robenv.environment.run_command import CommandAbortedError
from robenv.environment.run_command import CommandFailedError
from robenv.environment.run_command import run_command
from robenv.util.file_logger import write_log


_logger = getLogger(__name__)


class NoDownloadUrlError(Exception):
    def __init__(self, command: str) -> None:
        super().__init__(
            f"Command `{command}` did not return an apt link",
        )


class AddCommand(Command):
    name = "add"
    description = "Add debian package into the robenv"
    arguments = [
        argument(
            "name",
            description="If it's a ROS package this should be the "
            "non-translated package-name. Basically exactly what it's named "
            "in its package.xml",
            multiple=False,
        ),
        argument(
            "path_or_url",
            description="Path to the deb-file or url where to download it from",
            multiple=False,
            optional=True,
        ),
    ]
    options = [
        option(
            "overwrite",
            description="Overwrite (maybe) existing installation",
        ),
        option(
            "skip-dependency-check",
            description="Skip checking for dependencies of the deb-file",
        ),
    ]

    @staticmethod
    def _download_deb_file(url: str) -> Path:
        filename = Path(url).name
        _logger.info("Download %s from %s", filename, url)
        download = requests.get(url, allow_redirects=True, timeout=60)
        path = Path(f"dist/{filename}")
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(download.content)
        _logger.debug("saved %s at %s", filename, str(path))
        return path

    @staticmethod
    def _get_apt_url(package_name: str) -> str:
        _logger.info("Download via apt %s", package_name)

        command = f"/usr/bin/apt-get download {package_name!s} --print-uris"

        with TemporaryDirectory() as tmp_dir:
            output = run_command(f"bash -c '{command}'", events=None, cwd=Path(tmp_dir))

        if output == "":
            raise NoDownloadUrlError(command)

        split = output.split(" ")
        return split[0].replace("'", "")

    def _download(self, name_or_url: str) -> Path:
        url = name_or_url
        if "://" not in name_or_url:
            url = self._get_apt_url(name_or_url)
        return self._download_deb_file(url)

    def handle(self) -> int:
        robenv = RobEnv()
        package_name = self.argument("name")
        path_or_url = self.argument("path_or_url")
        check_dependencies = not self.option("skip-dependency-check")

        if path_or_url:
            if "://" in path_or_url:
                _logger.info("Installing from url: %s", path_or_url)
                deb_file_path = self._download(str(path_or_url))
            else:
                _logger.info("Installing from deb file path: %s", path_or_url)
                deb_file_path = Path(path_or_url)
        else:
            _logger.info("Installing from package name: %s", package_name)
            deb_file_path = self._download(str(package_name))

        if not deb_file_path.exists():
            _logger.error("deb file: %s doesn't exist", str(deb_file_path))
            return 3

        _logger.info("Installing %s", package_name)
        try:
            installable = Installable(package_name, DebName(deb_file_path.name), deb_file_path)
            robenv.install(installable, overwrite=self.option("overwrite"), check_dependencies=check_dependencies)
            _logger.info("install %s was successful", deb_file_path.name)
        except CommandAbortedError:
            _logger.exception("install %s aborted", package_name)
            return 2
        except CommandFailedError as e:
            _logger.exception("Command failed unexpectedly")
            write_log(robenv.path, package_name, e.output)
            _logger.exception("install %s failed", package_name)
            return 1
        # for NOTUSED see https://github.com/python-poetry/cleo/issues/130
        self.call("rosdep add", f"NOTUSED {package_name} {parse_filename(deb_file_path.name).name}")
        return 0
