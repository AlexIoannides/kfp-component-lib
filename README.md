# Packaging Reusable Kubeflow Pipeline Components

This repository demonstrates how reusable Kubeflow Pipeline components can be bundled together into a Python package and tested.

## Developing Python Components for Reuse

Python components for Kubeflow are standalone scripts that have been wrapped into a Python function and associated with a container image and the required Python package dependencies. For example,

```python
@dsl.component(
    base_image="python:3.10", packages_to_install=["numpy==1.26.*", "pandas==2.2.*"]
)
def make_numeric_dataset(n_rows: int, n_cols: int, data: dsl.Output[dsl.Dataset]) -> None:
    """Synthetic dataset generation pipeline component. """
    from numpy.random import default_rng
    from pandas import DataFrame

    rng = default_rng(42)
    dataset = DataFrame(
        {
            "y": rng.standard_normal(n_rows),
            "x1": rng.standard_normal(n_rows),
            "x2": rng.standard_normal(n_rows),
            "x3": rng.standard_normal(n_rows),
        }
    )
    dataset.to_parquet(data_out.path)
```

No code can be imported from outside the component definition and all dependencies need to be declared upfront. When developing multiple components this can get hard to test, manage and maintain. One way around this problem is to bundle all code into a Python package (e.g., `kfp_component_lib`), have the components import from this package, and then parametrise the base image required to run and test the component. For example,

```python
@dsl.component(
    base_image=KFP_CONTAINER_IMAGE, packages_to_install=["kfp_component_pipeline==0.1.0"]
)
def make_numeric_dataset(n_rows: int, n_cols: int, data: dsl.Output[dsl.Dataset]) -> None:
    """Synthetic dataset generation pipeline component. """
    from kfp_component_lib.datasets import generate_numeric_data

    dataset = generate_numeric_data(n_rows)
    dataset.to_parquet(data_out.path)
```

Where `generate_numeric_data` is defined as,

```python
from numpy.random import default_rng
from pandas import DataFrame


def generate_numeric_data(n_rows: int) -> DataFrame:
    """Generate a synthetic numerical dataframe."""
    rng = default_rng(42)
    dataset = DataFrame(
        {
            "y": rng.standard_normal(n_rows),
            "x1": rng.standard_normal(n_rows),
            "x2": rng.standard_normal(n_rows),
            "x3": rng.standard_normal(n_rows),
        }
    )
    return dataset
```

This has the following avantages:

* All dependencies can be managed centrally via the package's pyproject.toml file.
* The inner component logic can be easily tested (e.g., using Pytest).

### Writing Functional Tests

Components functionality can be tested using the Kubeflow Pipelines local execution runner - e.g.,

```python
import shutil

import pandas as pd
from kfp import local

from kfp_component_lib.components import make_numeric_dataset

_KFP_ROOT_DIR = "./kfp_outputs"

local.init(runner=local.SubprocessRunner(use_venv=False), pipeline_root=_KFP_ROOT_DIR)


def test_make_numeric_dataset_kfp_component():
    try:
        task = make_numeric_dataset(n_rows=10)
        output_dataset = pd.read_parquet(task.outputs["data_out"].path)
        assert output_dataset.shape == (10, 4)
    except Exception:
        assert False
    finally:
        shutil.rmtree(_KFP_ROOT_DIR, ignore_errors=True)
```

Which will replicate how Kubeflow Pipelines will run the component, albeit on the machine running the test. In this example the runner has been set to use a sub-process and the same virtual environment as the local development environment, but this can be changed to use a Docker runner or to use a sub-process that recreates a fresh virtual environment (be sure to build the package first using `nox -s build_and_deploy_pkg -- deploy=false`, if you want to use this option).

### Composing Pipelines

Once the package of components has been built, composing a pipeline is as easy as,

```python
from kfp import dsl

from kfp_component_lib.components import make_numeric_dataset


@dsl.pipeline
def synthetic_data_pipeline(n_rows: int = 1000) -> None:
    """Create synthetic datasets."""
    task_1 = make_numeric_dataset(n_rows=n_rows)
    task_2 = make_numeric_dataset(n_rows=n_rows)
    task_2.after(task_1)
```

Which can be compiled using,

```python
from kfp import compiler


compiler.Compiler().compile(
    pipeline_func=synthetic_data_pipeline, package_path="pipeline.json"
)
```

Ready for deployment!

### Baking the Package into a Container Image

If you would like to include the package into the image used to run the component (as opposed to pip-install it into a generic Python image), then we include a Dockerfile togther with the `build_and_deploy_container_image` Nox task, that demonstrates how to do this while keeping the image version synchronised with the Python package. In this instance the example component definition listed above becomes,

```python
@dsl.component(base_image=KFP_CONTAINER_IMAGE)
def make_numeric_dataset(n_rows: int, n_cols: int, data: dsl.Output[dsl.Dataset]) -> None:
    """Synthetic dataset generation pipeline component. """
    from kfp_component_lib.datasets import generate_numeric_data

    dataset = generate_numeric_data(n_rows)
    dataset.to_parquet(data_out.path)
```

I.e., the `packages_to_install` argument is no longer required (as the package has been already installed into the image). This has the advantage of crystalling all transitive dependencies so that reproducibility is easier to achieve.

## Developer Setup

Install the package as an [editable dependency](https://setuptools.pypa.io/en/latest/userguide/development_mode.html), together with all the developer tools required to format code, check types and run tests:

```text
$ pip install -e ".[dev]"
```

### Developer Task Execution with Nox

We use [Nox](https://nox.thea.codes/en/stable/) for scripting developer tasks, such as formatting code, checking types and running tests. These tasks are defined in `noxfile.py`, a list of which can be returned on the command line,

```text
$ nox --list

Sessions defined in /Users/.../noxfile.py:

* run_tests -> Run unit tests.
- format_code -> Lint code and re-format where necessary.
* check_code_formatting -> Check code for formatting errors.
* check_types -> Run static type checking.
- build_and_deploy_pkg -> Build wheel and deploy to PyPI.
- build_and_deploy_container_image -> Build container image and deploy to Docker Hub.

sessions marked with * are selected, sessions marked with - are skipped.
```

Single tasks can be executed easily - e.g.,

```text
$ nox -s run_tests

nox > Running session run_tests-3.10
nox > Creating virtual environment (virtualenv) using python3.10 in .nox/run_tests-3-10
nox > python -m pip install '.[dev]'
nox > pytest 
======================================== test session starts ========================================
platform darwin -- Python 3.10.2, pytest-7.4.2, pluggy-1.3.0
rootdir: /Users/.../kfp_component_lib
configfile: pyproject.toml
testpaths: tests
collected 1 item                                                                                                                                                         

tests/test_hello_world.py .                                                                                                                                        [100%]

========================================== 1 passed in 0.00s =========================================
nox > Session run_tests-3.10 was successful.
```

### Building Packages and Deploying to PyPI

This is automated via the `nox -s build_and_deploy_pkg` command. In order to use this, the following environment variables will need to be made available to Python:

```text
PYPI_USR  # PyPI username
PYPI_PWD  # PyPI password
```

These may be specified in a `.env` file from which they will be loaded automatically - e.g.,

```text
PYPI_USR=XXXX
PYPI_PWD=XXXX
```

Note that `.gitignore` will ensure that `.env`is not tracked by Git. You can also choose to build without deploying,

```text
nox -s build_and_deploy_pkg -- deploy=false
```

### Building Container Image and Deploying to Docker Hub

This is automated via the `nox -s build_and_container_image` command, which assumes that you have Docker running on your machine and logged into Docker Hub. You can also choose to build without deploying,

```text
nox -s build_and_deploy_container_image -- deploy=false
```

## CI/CD

This repo comes configured to run two [GitHub Actions](https://docs.github.com/en/actions) workflows:

- **Test Python Package (CI)**, defined in `.github/workflows/python-package-ci.yml`
- **Deploy Python Package (CD)**, defined in `.github/workflows/python-package-cd.yml`

The CI workflow has been configured to run whenever a pull request to the `main` branch is created. The CD workflow has been configured to run whenever a [release](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository) is created on GitHub.

Note, the CD workflow will require `PYPI_USR` and `PYPI_PWD` to be added as [repository secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions).
