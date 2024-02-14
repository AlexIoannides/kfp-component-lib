"""Kubeflow Pipeline components for working with data."""
from kfp import dsl
from numpy.random import default_rng
from pandas import DataFrame

from kfp_component_lib import KFP_COMPONENTS_IMAGE


def _make_numeric_dataset(n_rows: int) -> DataFrame:
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


@dsl.component(base_image=KFP_COMPONENTS_IMAGE)
def make_numeric_dataset(n_rows: int, data_out: dsl.Output[dsl.Dataset]) -> None:
    """Generate a synthetic numerical dataset and save as Parquet file."""
    from kfp_component_lib.datasets import _make_numeric_dataset

    dataset = _make_numeric_dataset(n_rows)
    dataset.to_parquet(data_out.path)
