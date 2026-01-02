import json
import os
import subprocess
from pathlib import Path
from typing import Any
from typing import Callable
from typing import Iterator
from typing import Self

import pytest
from _pytest.scope import _ScopeName

from .commands import run

DEFAULT_STAGE = "default"

type TFVars = dict[str, str]


class TerraformOutputs:
    def __init__(self, data: Any) -> None:
        self._data = data

    @classmethod
    def load(cls, state_dir: Path) -> Self:
        cmd = ["terraform", "output", "-json"]
        output = subprocess.check_output(cmd, cwd=state_dir.as_posix())
        return cls(json.loads(output))

    def __getitem__(self, key: str) -> Any:
        try:
            item = self._data[key]
        except KeyError:
            raise KeyError(f"Terraform output {self!r} doesn't have {key=!r}") from None

        value = item["value"]
        return value

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def __repr__(self) -> str:
        outputs = sorted(self._data.keys())
        return f"TerraformOutput({outputs=})"


class TerraformWorkspace:
    def __init__(
        self,
        state_dir: Path,
        *,
        stage: str = DEFAULT_STAGE,
    ) -> None:
        self.state_dir = state_dir
        self.stage = stage

        self.SKIP_APPLY_VAR = f"SKIP_{self.stage}_APPLY"
        self.SKIP_DESTROY_VAR = f"SKIP_{self.stage}_DESTROY"

    @property
    def skip_apply(self) -> bool:
        return bool(os.environ.get(self.SKIP_APPLY_VAR))

    @property
    def skip_destroy(self) -> bool:
        return bool(os.environ.get(self.SKIP_DESTROY_VAR))

    def init(self) -> Self:
        cmd = ["terraform", "init"]
        run(cmd, self.state_dir)
        return self

    def apply(self, tfvars: TFVars | None = None, *, force: bool = True) -> Self:
        if not force and self.skip_apply:
            print(
                f"Skipping 'terraform apply' due to environment variable {self.SKIP_APPLY_VAR!r}"
            )
            return self

        if tfvars is None:
            tfvars = {}

        cmd = ["terraform", "apply", "-auto-approve", "-input=false"]
        for key, value in tfvars.items():
            cmd.extend(["-var", f"{key}={value}"])

        run(cmd, self.state_dir)
        return self

    def destroy(self, *, force: bool = True) -> None:
        if not force and self.skip_destroy:
            print(
                f"Skipping 'terraform destroy' due to environment variable {self.SKIP_DESTROY_VAR!r}"
            )
            return

        cmd = ["terraform", "destroy", "-auto-approve", "-input=false"]
        run(cmd, self.state_dir)

    def __enter__(self) -> Self:
        self.init()
        self.apply(force=False)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: Any,
    ) -> None:
        self.destroy(force=False)

    def output(self) -> TerraformOutputs:
        return TerraformOutputs.load(self.state_dir)

    @classmethod
    def as_fixture(
        cls,
        cwd: str,
        *,
        scope: _ScopeName,
        stage: str = DEFAULT_STAGE,
    ) -> Callable[..., Iterator[Self]]:
        @pytest.fixture(scope=scope)
        def terraform_fixture_impl() -> Iterator[TerraformWorkspace]:
            with TerraformWorkspace(Path(cwd), stage=stage) as tf:
                yield tf

        return terraform_fixture_impl
