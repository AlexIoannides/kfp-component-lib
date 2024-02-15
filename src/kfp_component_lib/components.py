"""Kubeflow Pipeline components for working with data."""
from kfp import dsl

from kfp_component_lib import KFP_CONTAINER_IMAGE, PKG_DEPENDENCY


@dsl.component(base_image=KFP_CONTAINER_IMAGE, packages_to_install=PKG_DEPENDENCY)
def make_numeric_dataset(n_rows: int, data_out: dsl.Output[dsl.Dataset]) -> None:
    """Generate a synthetic numerical dataset and save as Parquet file."""
    from kfp_component_lib.datasets import generate_numeric_data

    dataset = generate_numeric_data(n_rows)
    dataset.to_parquet(data_out.path)
