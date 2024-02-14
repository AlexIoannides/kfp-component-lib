"""Functional tests for KFP components."""
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
