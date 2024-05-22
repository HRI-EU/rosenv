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

from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import NewType

from defusedxml import ElementTree


PackageName = NewType("PackageName", str)


class PackageXMLNotExistsError(Exception):
    def __init__(self, path: Path) -> None:
        self.path = path
        super().__init__(f"package.xml at '{path!s}' doesn't exist!")


class UnrecognizedPackageFormatError(Exception):
    def __init__(self, path: Path, *tags: str) -> None:
        self.tags = tags
        super().__init__(f"package.xml at '{path!s}' contains unrecognized tags: {tags}")


@dataclass
class ExternalDependency:
    name: PackageName
    required_by: list[ROSPackage]


@dataclass
class ROSPackage:
    name: PackageName
    path: Path
    version: str

    _package_xml: ElementTree = field(repr=False)

    @classmethod
    def from_project(cls, project: Path) -> ROSPackage:
        package_file = project.absolute() / "package.xml"

        if not package_file.exists():
            raise PackageXMLNotExistsError(package_file)

        package_root = ElementTree.parse(str(package_file)).getroot()

        if package_root.tag != "package":
            raise UnrecognizedPackageFormatError(package_file, package_root.tag)

        name = None
        version = None

        for child in package_root:
            if child.tag == "name":
                name = child.text
            elif child.tag == "version":
                version = child.text

            if None not in (name, version):
                break

        if name is None or version is None:
            raise UnrecognizedPackageFormatError(package_file, "not name", "not version")

        return ROSPackage(
            name=name,
            path=project.absolute(),
            version=version,
            _package_xml=package_root,
        )

    def get_build_dependencies(self) -> list[str]:
        return [tag.text for tag in self._package_xml.findall("build_depend") + self._package_xml.findall("depend")]

    def get_exec_dependencies(self) -> list[str]:
        return [tag.text for tag in self._package_xml.findall("exec_depend") + self._package_xml.findall("depend")]

    def is_metapackage(self) -> bool:
        return self._package_xml.find(".//metapackage") is not None
