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

from unittest.mock import MagicMock

import pytest

from pytest_mock import MockFixture

from robenv.util.cpu_count import get_cpu_count


@pytest.fixture()
def cpu_count_mock(mocker: MockFixture) -> MagicMock:
    return mocker.patch("robenv.util.cpu_count.cpu_count")


def test_cpu_count_should_give_cpu_count_from_os(cpu_count_mock: MagicMock) -> None:
    expected_cpu_count = 4
    cpu_count_mock.return_value = expected_cpu_count

    assert get_cpu_count() == expected_cpu_count


def test_cpu_count_should_give_minimum_if_count_is_lower(cpu_count_mock: MagicMock) -> None:
    cpu_count_mock.return_value = 2

    minimum = 4
    assert get_cpu_count(minimum=minimum) == minimum


def test_cpu_count_should_give_minimum_if_count_none(cpu_count_mock: MagicMock) -> None:
    cpu_count_mock.return_value = None

    minimum = 4
    assert get_cpu_count(minimum=minimum) == minimum
