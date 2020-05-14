import time
import contextlib


class retry:
    def __init__(self, message, attempts=60, interval=2):
        self.message = message
        self.attempts = attempts
        self.interval = interval
        self.ok = False

    def __call__(self, callback, *args, **kwargs):
        for catcher in self:
            with catcher:
                callback(*args, **kwargs)

    def __iter__(self):
        print("{}: starting".format(self.message))

        nb_attempts = 0
        while not self.ok:
            nb_attempts += 1

            yield self.catcher()

            if not self.ok:
                if nb_attempts > self.attempts:
                    assert False, "{}: failed after {} attempts, giving up".format(self.message, self.attempts)

                print("{}: try {}/{} failed, will retry in {} seconds".format(self.message, nb_attempts, self.attempts, self.interval))
                time.sleep(self.interval)


    @contextlib.contextmanager
    def catcher(self):
        try:
            yield
        except Exception as exc:
            print("{}: failed with: {}".format(self.message, exc))
            self.ok = False
        else:
            self.ok = True
