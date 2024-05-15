#!/usr/bin/env python
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

import subprocess  # noqa: S404
import sys

from argparse import ArgumentParser
from argparse import RawTextHelpFormatter


def main() -> None:
    arg_parse = ArgumentParser(
        formatter_class=RawTextHelpFormatter,
        epilog=f"""Examples:
    Run collect only:
        {sys.argv[0]} -- --collect-only
""",
    )
    arg_parse.add_argument(
        "--coverage",
        action="store_true",
        help="Enable coverage scanning",
    )
    arg_parse.add_argument(
        "--junit",
        type=str,
        metavar="JUNIT_FILE",
        help="Write junit result file",
    )
    arg_parse.add_argument(
        "pytest_options",
        metavar="PYTEST_OPTIONS",
        nargs="*",
        type=str,
        help="preface with '--' to give pytest more custom options",
    )

    args = arg_parse.parse_args()

    coverage_options = (
        [
            "--cov-branch",
            "--cov-report=term",
            "--cov-report=html",
            "--cov-report=xml",
            "--cov=src",
        ]
        if args.coverage
        else []
    )
    junit = [f"--junitxml={args.junit}"] if args.junit else []
    custom_options: list[str] = args.pytest_options or []

    try:
        subprocess.run(
            [  # noqa: S603, S607
                "poetry",
                "run",
                "pytest",
                "--verbose",
                "tests/integration",
                *coverage_options,
                *junit,
                *custom_options,
            ],
            check=True,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
    except subprocess.CalledProcessError as e:
        print(str(e))
        raise SystemExit(e.returncode) from e


if __name__ == "__main__":
    main()
