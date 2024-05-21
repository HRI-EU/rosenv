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

import subprocess
import sys

from argparse import ArgumentParser
from argparse import RawTextHelpFormatter


def main() -> None:
    arg_parse = ArgumentParser(
        formatter_class=RawTextHelpFormatter,
        epilog=f"""Examples:
    Run with unsafe-fixes:
        {sys.argv[0]} -- --unsafe-fixes

    Run but ignore single rule, e.g. T201/`print` detection:
        {sys.argv[0]} -- --ignore T201
""",
    )
    arg_parse.add_argument(
        "--check",
        action="store_true",
        help="Only check for errors, don't fix them",
    )
    arg_parse.add_argument(
        "--output-format",
        type=str,
        help="Use specific output-format, for best result use --output as well",
    )
    arg_parse.add_argument("--output", type=str, help="Use specific output file")
    arg_parse.add_argument(
        "files",
        metavar="FILES",
        nargs="*",
        type=str,
        default=["."],
        help="files to check, if you preface this with '--' you can expand the ruff command options",
    )

    args = arg_parse.parse_args()

    check_option = [] if args.check else ["--fix"]
    output_file_options = ["--output-file", args.output] if args.output else []
    output_format_options = ["--output-format", args.output_format] if args.output_format else []

    try:
        subprocess.run(
            [  # noqa: S603, S607
                "poetry",
                "run",
                "ruff",
                "check",
                *check_option,
                *output_file_options,
                *output_format_options,
                *args.files,
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
