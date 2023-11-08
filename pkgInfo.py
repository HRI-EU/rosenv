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


name = "rosenv"
sqLevel = "basic"

copyright = {  # noqa: A001
    ".": "Copyright (c) Honda Research Institute Europe GmbH",
    "./tests/resources/example_project_ros1": [""],
    "./tests/resources/example_project_ros2": [""],
}

sqOptOutRules = [
    "PY02",
    "DOC03",
]
sqComments = {
    "PY02": "Private static methods can only be referenced with full class name (all messages are false positives)",
    "DOC03": "Usage explained in README.md",
}

sqOptOutDirs = [".venv"]

scripts = {"unittest": "ci-unit-test.sh"}

pylintConf = "pyproject.toml"
