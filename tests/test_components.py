"""Functional tests for KFP components.

These tests use the KFP local executor to test the components as if they were running in
 a KFP container. The runner has been set to use a sub-process and the same virtual
environment as the local dev environment, but this can be changed to use a Docker runner
or to use a sub-process that recreates a fresh virtual environment (be sure to build the
package first using `nox -s build_and_deploy_pkg -- deploy=false`).
"""
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
