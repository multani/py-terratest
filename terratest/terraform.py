import json
import os
import subprocess
from typing import Any
from typing import Iterator


def fixture(
    stage_name: str, directory: str, tf_vars: dict[str, Any] | None = None
) -> Iterator[None]:
    if tf_vars is None:
        tf_vars = {}

    SKIP_APPLY_VAR = f"SKIP_{stage_name}_APPLY"
    SKIP_DESTROY_VAR = f"SKIP_{stage_name}_DESTROY"

    skip_apply = bool(os.environ.get(SKIP_APPLY_VAR))
    skip_destroy = bool(os.environ.get(SKIP_DESTROY_VAR))

    if skip_apply:
        msg = f"{SKIP_APPLY_VAR} set, skipping applying Terraform for {stage_name}"
        print(msg)
    else:
        cmd = ["terraform", "init"]
        print(f"Running: {cmd} (PWD={directory})")
        subprocess.run(cmd, cwd=directory)

        cmd = ["terraform", "apply", "-input=false", "-auto-approve", "-lock=false"]

        for key, value in sorted(tf_vars.items()):
            cmd.extend(["-var", f"{key}={value}"])

        print(f"Running: {cmd} (PWD={directory})")
        subprocess.run(cmd, cwd=directory)

    # Yield into the caller
    yield

    if skip_destroy:
        msg = f"{SKIP_DESTROY_VAR} set, skipping destroying Terraform for {stage_name}"
        print(msg)
    else:
        cmd = ["terraform", "destroy", "-auto-approve"]

        for key, value in sorted(tf_vars.items()):
            cmd.extend(["-var", f"{key}={value}"])

        print(f"Running: {cmd} (PWD={directory})")
        subprocess.run(cmd, cwd=directory)


class OutputWrapper:
    def __init__(self, data: Any) -> None:
        self._data = data

    def __getitem__(self, key: str) -> Any:
        value = self._data[key]["value"]
        return value


def load_outputs(directory: str) -> OutputWrapper:
    cmd = ["terraform", "output", "-json"]
    output = subprocess.check_output(cmd, cwd=directory)
    return OutputWrapper(json.loads(output))
