"""Tests that components can be assembled into pipeline DAGs that compile."""
from pathlib import Path

from kfp import compiler, dsl

from kfp_component_lib.components import make_numeric_dataset


@dsl.pipeline
def synthetic_data_pipeline(n_rows: int = 1000) -> None:
    """Create synthetic datasets."""
    task_1 = make_numeric_dataset(n_rows=n_rows)
    task_2 = make_numeric_dataset(n_rows=n_rows)
    task_2.after(task_1)


def test_synthetic_data_pipeline_compiles():
    compiled_pipeline_file = "pipeline.json"
    try:
        compiler.Compiler().compile(
            pipeline_func=synthetic_data_pipeline, package_path=compiled_pipeline_file
        )
        assert True
    except Exception:
        assert False
    finally:
        compiled_pipeline_path = Path(compiled_pipeline_file)
        if compiled_pipeline_path.exists():
            compiled_pipeline_path.unlink()
