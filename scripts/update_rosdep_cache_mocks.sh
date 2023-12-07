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

HIGHLIGHT="$(tput setaf 207)"
WARN="$(tput setaf 202)"
NORMAL="$(tput sgr0)"

log() {
    echo -e "\n${HIGHLIGHT}$*${NORMAL}\n"
}

errorLog() {
    echo -e "\n${WARN}$*${NORMAL}\n" >&2
}

updateRosdepMocks() {
    example_project="${PWD}/tests/resources/example_project_ros1"
    if [[ ! -d ${example_project} ]]; then
        errorLog "Couldn't find example_project at: ${example_project}"
        exit 1
    fi

    mock_location="${PWD}/tests/resources/rosdep_mocks"
    (
        log "Initializing rosenv in example_project..."
        cd "$example_project" || exit 1

        if ! poetry run rosenv init; then
            errorLog "Initializing rosenv failed, aborting..."
            exit 2
        fi

        poetry run rosenv rosdep add nodeps nodeps
        poetry run rosenv rosdep add dep-on-nodeps dep-on-nodeps --run-update

        rosdep_cache="${PWD}/rosenv/cache/ros/rosdep/"
        if [[ ! -d ${rosdep_cache} ]]; then
            errorLog "Couldn't find rosdep cache files at: ${rosdep_cache}"
            exit 3
        fi

        log "Clearing original rosdep_mocks"
        rm -rfv "${mock_location}/meta.cache" "${mock_location}/sources.cache"

        log "Copying new mocks into place"
        cp -rv "$rosdep_cache"/* "$mock_location"

        log "Deleting created rosenv"
        rm -rf rosenv
    )

    log "Update done, don't forget to commit the update"
}

updateIndexFileMock() {
    log "Updating rosdistro index file..."

    index_mock="${PWD}/tests/resources/rosdistro_index/index-v4.yaml"

    curl \
        --show-error \
        --silent \
        --location \
        https://raw.githubusercontent.com/ros/rosdistro/master/index-v4.yaml \
        >"$index_mock"

    log "Update done, don't forget to commit the update"
}

updateRosdepMocks
updateIndexFileMock
