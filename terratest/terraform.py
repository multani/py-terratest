import json
import os
import subprocess


def fixture(stage_name, directory, tf_vars=None):
    if tf_vars is None:
        tf_vars = {}

    SKIP_APPLY_VAR = "SKIP_{}_APPLY".format(stage_name)
    SKIP_DESTROY_VAR = "SKIP_{}_DESTROY".format(stage_name)

    skip_apply = bool(os.environ.get(SKIP_APPLY_VAR))
    skip_destroy= bool(os.environ.get("SKIP_{}_DESTROY".format(stage_name)))

    if skip_apply:
        print("{} set, skipping applying Terraform for {}".format(SKIP_APPLY_VAR, stage_name))
    else:
        cmd = ["terraform", "init"]
        print("Running: {} (PWD={})".format(cmd, directory))
        subprocess.run(cmd, cwd=directory)

        cmd = ["terraform", "apply", "-input=false", "-auto-approve", "-lock=false"]

        for key, value in sorted(tf_vars.items()):
            cmd.extend(["-var", "{}={}".format(key, value)])

        print("Running: {} (PWD={})".format(cmd, directory))
        subprocess.run(cmd, cwd=directory)

    # Yield into the caller
    yield

    if skip_destroy:
        print("{} set, skipping destroying Terraform for {}".format(SKIP_DESTROY_VAR, stage_name))
    else:
        cmd = ["terraform", "destroy", "-auto-approve"]

        for key, value in sorted(tf_vars.items()):
            cmd.extend(["-var", "{}={}".format(key, value)])

        print("Running: {} (PWD={})".format(cmd, directory))
        subprocess.run(cmd, cwd=directory)


def load_outputs(directory):
    cmd = ["terraform", "output", "-json"]
    output = subprocess.check_output(cmd, cwd=directory)

    class OutputWrapper:
        def __init__(self, data):
            self._data = data

        def __getitem__(self, key):
            value = self._data[key]["value"]
            return value

    return OutputWrapper(json.loads(output))
