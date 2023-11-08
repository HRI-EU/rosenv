#!/bin/bash
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

set -euo pipefail

usage() {
    cat <<EOF
usage: $0 [major|minor|patch]
    Script to help with release creation and automation of the tasks surrounding
    a release. Mainly, raising the version numbers and correctly tagging the
    versions.

    The script will also immediately push the tags and commits.

    So this works correctly it can only be executed with a clean working-tree
    and the 'main' branch.

    Script has two modes, interactive or scripted.

    Interactive:
        # call without arguments
        $0

        The scripts asks some questions to determine the 'right' next version
        number and also provides a fallback.

    Scripted:
        # call with [marjor|minor|patched]
        $0 major

        Script will give you the version change you requested (if possible).
EOF
}

verify_current_branch() {
    current_branch=$(git branch --show-current)

    [[ ${current_branch} == main ]]
}

verify_clean_working_tree() {
    git diff --quiet
}

check_yes() {
    read -r -p "$1 (y|n): " -n 1 yes_no
    echo "" >&2

    [[ ${yes_no} == y ]]
}

ask_for_rule() {
    rule=$1

    if [[ -n ${rule} ]]; then
        echo "${rule}"
    else
        echo -e "Compared to the last release...\n" >&2
        if check_yes "do you have breaking changes?"; then
            echo "major"
        elif check_yes "do you have new features?"; then
            echo "minor"
        elif check_yes "did you only correct a broken behavior?"; then
            echo "patch"
        else
            read -r -p "Please provide a rule for the next release [major,minor,patch]: " rule
            echo "${rule}"
        fi
    fi
}

release() {
    rule=$1

    poetry version "${rule}"
    tag_version=$(poetry version --short)

    git add pyproject.toml
    git commit -m "Prepare release: ${tag_version}"
    git tag "${tag_version}" -m "Release version: ${tag_version}"
}

prerelease() {
    poetry version "prerelease"

    git add pyproject.toml
    git commit -m "Prepare for next development iteration"
}

if [[ ${1:-} == "-h" ]] || [[ ${1:-} == "--help" ]]; then
    usage
    exit 1
fi

verify_current_branch || {
    echo "Releases can only be created on main branch!" >&2
    exit 1
}

verify_clean_working_tree || {
    echo "You have unstaged changes, please commit or stash them." >&2
    exit 1
}

rule=$(ask_for_rule "${1:-}")
echo -e "\n\tReleasing ${rule}\n"

release "${rule}"
prerelease

git push
git push --tags
