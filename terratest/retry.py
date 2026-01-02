import time
from contextlib import AbstractContextManager
from contextlib import contextmanager
from typing import Any
from typing import Callable
from typing import Iterator


class retry:
    def __init__(self, message: str, attempts: int = 60, interval: int = 2) -> None:
        self.message = message
        self.attempts = attempts
        self.interval = interval
        self.ok = False

    def __call__(
        self, callback: Callable[[Any], Any], *args: Any, **kwargs: Any
    ) -> None:
        for catcher in self:
            with catcher:
                callback(*args, **kwargs)

    def __iter__(self) -> Iterator[AbstractContextManager[None]]:
        prefix = f"{self.message}: "
        print(
            f"{prefix}starting, will try with attemps={self.attempts}, interval={self.interval}s"
        )
        start_time = time.time()

        nb_attempts = 0
        while not self.ok:
            nb_attempts += 1
            prefix = f"{self.message} [{nb_attempts}/{self.attempts}]: "

            yield self.catcher()

            if not self.ok:
                if nb_attempts > self.attempts:
                    msg = f"{prefix}failed after {self.attempts} attempts, giving up"
                    assert False, msg

                msg = f"{prefix}failed, will retry in {self.interval} seconds"
                print(msg)
                time.sleep(self.interval)

        stop_time = time.time()
        elapsed_time = int(stop_time - start_time)
        print(f"{prefix}success! (after {elapsed_time} seconds)")

    @contextmanager
    def catcher(self) -> Iterator[None]:
        try:
            yield
        except Exception as exc:
            print(f"{self.message}: failed with: {exc}")
            self.ok = False
        else:
            self.ok = True
