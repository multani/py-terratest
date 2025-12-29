import contextlib
import time
from typing import Any
from typing import Callable
from typing import Iterator


class retry:
    def __init__(self, message: str, attempts: int = 60, interval: int = 2) -> None:
        self.message = message
        self.attempts = attempts
        self.interval = interval
        self.ok = False

    def __call__(self, callback: Callable[[Any], Any], *args: Any, **kwargs: Any) -> None:
        for catcher in self:
            with catcher:
                callback(*args, **kwargs)

    def __iter__(self) -> Iterator[contextlib.AbstractContextManager[None]]:
        print(f"{self.message}: starting")

        nb_attempts = 0
        while not self.ok:
            nb_attempts += 1

            yield self.catcher()

            if not self.ok:
                if nb_attempts > self.attempts:
                    msg = f"{self.message}: failed after {self.attempts} attempts, giving up"
                    assert False, msg

                msg = f"{self.message}: try {nb_attempts}/{self.attempts} failed, will retry in {self.interval} seconds"
                print(msg)
                time.sleep(self.interval)

    @contextlib.contextmanager
    def catcher(self) -> Iterator[None]:
        try:
            yield
        except Exception as exc:
            print(f"{self.message}: failed with: {exc}")
            self.ok = False
        else:
            self.ok = True
