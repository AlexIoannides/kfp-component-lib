"""Tests for KFP dataset components."""
import numpy as np

from kfp_component_lib.datasets import generate_numeric_data


def test_make_numeric_dataset():
    dataset = generate_numeric_data(n_rows=1000)
    assert dataset.shape == (1000, 4)
    assert dataset.columns.tolist() == ["y", "x1", "x2", "x3"]
    np.testing.assert_almost_equal(np.average(dataset["y"].to_numpy()), 0.0, decimal=1)
