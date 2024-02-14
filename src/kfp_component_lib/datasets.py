"""Classes and functions for composing KFP components that work on datasets."""
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
