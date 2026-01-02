import shlex
from subprocess import CompletedProcess


class TerratestError(Exception):
    """Base exception for all Terratest-related errors."""

    pass


class CommandError(TerratestError):
    def __init__(
        self, command: list[str], cwd: str, result: CompletedProcess[str]
    ) -> None:
        super().__init__()

        self.command = command
        self.cwd = cwd
        self.result = result

    def __str__(self) -> str:
        message = f"Command {shlex.join(self.command)!r} failed in {self.cwd!r}"
        output_str = self.result.stderr
        return f"{message}:\n{output_str}"
