from pathlib import Path

from terratest.terraform import TerraformWorkspace

HERE = Path(__file__).parent.resolve()
FIXTURE = HERE / "fixtures/tf/local-file"

tf = TerraformWorkspace.as_fixture(FIXTURE.as_posix(), scope="module", stage="tf-local-file")


def test_1(tf: TerraformWorkspace) -> None:
    test_file = tf.state_dir / "test.txt"
    assert test_file.exists()
    assert test_file.read_text() == "foo"

    output = tf.output()

    assert "filename" in output
    assert Path(output["filename"]).name == "test.txt"


def test_2(tf: TerraformWorkspace) -> None:
    test_file = tf.state_dir / "test.txt"
    test_file.unlink(missing_ok=True)

    tfvars = {"content": "bar"}
    tf.apply(tfvars=tfvars)

    assert test_file.exists()
    assert test_file.read_text() == "bar"
