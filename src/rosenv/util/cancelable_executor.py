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

import signal

from concurrent.futures import Executor
from concurrent.futures import Future
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from types import FrameType
from types import TracebackType
from typing import Any
from typing import Callable
from typing import ClassVar
from typing import TypeVar

from typing_extensions import ParamSpec
from typing_extensions import Self


Params = ParamSpec("Params")
T = TypeVar("T")


class CancelableExecutor:
    """
    PoolExecutor with the same API but able to cancel it's futures on shutdown.

    This enables faster shutdowns of the entire pool without regard of waiting
    until _all_ futures are finished. If you want even faster shutdowns take
    care that your submitted work listens for `CancelableExecutor.cancel_event`
    and interrupts its work if the Event is set.
    """

    cancel_event: ClassVar[Event] = Event()

    def __init__(self, *, max_workers: int) -> None:
        self._pool: Executor = ThreadPoolExecutor(max_workers=max_workers)
        self._futures: list[Future[Any]] = []
        self._signal_handler: Callable[[int, FrameType | None], None] | int | None = None
        self._original_handler: Callable[[int, FrameType | None], None] | int | None = None

    def _handle_interrupt(self, _: int, __: FrameType | None) -> None:
        for future in self._futures:
            future.cancel()

        self.cancel_event.set()
        self.__exit__(None, None, None)

    def __enter__(self) -> Self:
        self._original_handler = signal.getsignal(signal.SIGINT)
        self._signal_handler = signal.signal(signal.SIGINT, self._handle_interrupt)
        return self

    def submit(
        self,
        fct: Callable[Params, T],
        *args: Params.args,
        **kwargs: Params.kwargs,
    ) -> Future[T]:
        f = self._pool.submit(fct, *args, **kwargs)
        self._futures.append(f)
        return f

    def __exit__(
        self,
        exctype: type[BaseException] | None,
        value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self._pool.__exit__(exctype, value, traceback)
        signal.signal(signal.SIGINT, self._original_handler)
