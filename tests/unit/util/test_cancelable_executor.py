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

import os
import signal

import pytest

from robenv.util.cancelable_executor import CancelableExecutor
from tests.conftest import YieldFixture


@pytest.fixture(autouse=True)
def _reset_cancel_event() -> YieldFixture[None]:
    yield

    CancelableExecutor.cancel_event.clear()


def send_interrupt() -> None:
    os.kill(os.getpid(), signal.SIGINT)


def test_cancelable_executor_should_set_cancel_flag_on_interrupt() -> None:
    assert not CancelableExecutor.cancel_event.is_set()

    with CancelableExecutor(max_workers=1) as pool:
        pool.submit(lambda: CancelableExecutor.cancel_event.wait(1))
        send_interrupt()

    assert CancelableExecutor.cancel_event.is_set()


def test_cancelable_executor_should_cancel_futures_on_interrupt() -> None:
    with CancelableExecutor(max_workers=1) as pool:
        futures = [pool.submit(lambda: CancelableExecutor.cancel_event.wait(1)) for _ in range(5)]
        send_interrupt()

    assert not futures[0].cancelled()
    assert all(f.cancelled() for f in futures[1:])


def test_cancelable_executor_should_not_allow_submits_after_interrupt() -> None:
    with CancelableExecutor(max_workers=1) as pool:
        pool.submit(lambda: None)
        send_interrupt()
        with pytest.raises(RuntimeError) as error:
            pool.submit(lambda: None)

        error.match("cannot schedule new futures after shutdown")
