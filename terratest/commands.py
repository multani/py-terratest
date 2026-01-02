import shlex
import subprocess
from pathlib import Path

from .exceptions import CommandError


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    root_dir = cwd.as_posix()
    print(f"Running: {shlex.join(cmd)!r} with cwd={root_dir!r}")
    result = subprocess.run(cmd, cwd=root_dir, capture_output=True, text=True)

    if result.returncode != 0:
        raise CommandError(cmd, root_dir, result)

    print(result.stdout)
    return result
