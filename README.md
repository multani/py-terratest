# A Terratest-like test library for Python

This is a [Terratest](https://terratest.gruntwork.io/)-like library containing
helpers for testing infrastructure.

> [!WARNING]
>  It's a proof-of-concept, work-in-progress, not tested code.
>
>  So use at your own risk.
>
> Use [Terratest](https://terratest.gruntwork.io/) instead: it's more mature, has
> more features, is tested, has a bigger community, etc.


## Why?

Wny not. I wanted to see how expressive my tests written using Terratest would
have been in Python.


## How to use?

It's good to use it with [pytest](https://docs.pytest.org/)!

### Terraform helpers

`terratest.terraform.fixture` can be used to prepare [pytest
fixtures](https://docs.pytest.org/en/latest/fixture.html):


```python
import pytest
from terratest import terraform

@pytest.fixture
def terraform_web_server():
    stage_name = "setup-server"
    directory = "../web-server"
    tf_vars = {
        "instance_type": "t3.medium",
    }

    yield from terraform.fixture(stage_name, directory, tf_vars)
```

This will run Terraform in the specified directory:

* `terraform init` and `terraform apply` will be run as a test setup
* `terraform destroy` will be run as a test teardown

The `apply` and `destroy` phases can be skipped using the following environment
variables:

* `SKIP_${stage_name}_APPLY`: will skip the `apply` phase
* `SKIP_${stage_name}_DESTROY`: will skip the `destroy` phase

This fixture can be chained together:

```python
import pytest
from terratest import terraform

@pytest.fixture
def terraform_vpc():
    yield from terraform.fixture("vpc", "../aws-vpc")

@pytest.fixture
def terraform_web_server(terraform_vpc):
    yield from terraform.fixture("setup-server", "../web-server")


def test_foobar(terraform_web_server):
    # The VPC will be created, then the web server
    # Tear down will be in the reversed order.
```

---

`terratest.terraform.load_outputs` loads as a dictionary the outputs from a
Terraform state:

```python
from terratest import terraform

def test_foobar(terraform_web_server):
    # ...

    output = terraform.load_outputs("../web-server")
    public_ip = output["public_ip"]

    #...
```


### AWS helpers

`terratest.aws.get_instance_ids_for_asg` returns the instance IDs of the
specified AWS autoscaling group:

```python
from terratest import aws

def test_foo():
    # ...

    region = "eu-central-1"
    asg = "my-autoscaling-group"
    instance_ids = aws.get_instance_ids_for_asg(asg, region)

    assert "i-123456789123" == instance_ids[0]
```

---

`terratest.aws.get_public_ip_of_ec2_instance` returns the public IP address of
the specified AWS instance:

```python
from terratest import aws

def test_foo():
    # ...

    region = "eu-central-1"
    instance_id = "i-123456789123"
    public_ip = aws.get_public_ip_of_ec2_instance(instance_id, region)

    assert "8.8.8.8" != public_ip
```


### Retrying tests

`terratest.retry.retry` retries a block of code until it succeed or until a
timeout expires:

```python
from terratest.retry import retry
import random

def test_foo():
    attempts = 10 # times
    interval = 1  # seconds

    for error_catcher in retry("rolling dices", attempts, interval):
        with error_catcher: # will catch any error in the block below
            assert random.randint(0, 100) < 50, "not lucky yet"
```

If you prefer calling functions, you can use:

```python
from terratest.retry import retry
import random

def test_foo():
    attempts = 10 # times
    interval = 0.1 # seconds

    def testing_dice(dice_size, chance):
        assert random.randint(0, dice_size) < chance, "not lucky yet"

    size = 6
    chance = 3
    retry("rolling dices", attempts, interval)(testing_dice, size, chance)
```
