import pandas as pd
import pytest
from pytest import param


@pytest.mark.parametrize('distinct', [False, True])
@pytest.mark.notimpl(["clickhouse", "datafusion"])
def test_union(backend, alltypes, df, distinct):
    result = alltypes.union(alltypes, distinct=distinct).execute()
    expected = df if distinct else pd.concat([df, df], axis=0)

    # Result is not in original order on PySpark backend when distinct=True
    result = result.sort_values(['id'])
    expected = expected.sort_values(['id'])

    backend.assert_frame_equal(result, expected)


@pytest.mark.parametrize(
    'distinct',
    [
        False,
        param(
            True,
            marks=pytest.mark.notimpl(
                ["duckdb", "postgres", "pyspark"],
                reason="Result order not guaranteed when distinct=True",
            ),
        ),
    ],
)
@pytest.mark.notimpl(["clickhouse", "datafusion"])
def test_union_no_sort(backend, alltypes, df, distinct):
    result = alltypes.union(alltypes, distinct=distinct).execute()
    expected = df if distinct else pd.concat([df, df], axis=0)

    backend.assert_frame_equal(result, expected)
