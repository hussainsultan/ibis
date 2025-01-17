import pandas as pd
import pandas.util.testing as tm
import pytest

import ibis
from ibis.expr import datatypes as dt


def test_whole_schema():
    customers = ibis.table(
        [
            ('cid', 'int64'),
            ('mktsegment', 'string'),
            (
                'address',
                (
                    'struct<city: string, street: string, '
                    'street_number: int32, zip: int16>'
                ),
            ),
            ('phone_numbers', 'array<string>'),
            (
                'orders',
                """array<struct<
                                oid: int64,
                                status: string,
                                totalprice: decimal(12, 2),
                                order_date: string,
                                items: array<struct<
                                    iid: int64,
                                    name: string,
                                    price: decimal(12, 2),
                                    discount_perc: decimal(12, 2),
                                    shipdate: string
                                >>
                            >>""",
            ),
            (
                'web_visits',
                (
                    'map<string, struct<user_agent: string, '
                    'client_ip: string, visit_date: string, '
                    'duration_ms: int32>>'
                ),
            ),
            (
                'support_calls',
                (
                    'array<struct<agent_id: int64, '
                    'call_date: string, duration_ms: int64, '
                    'issue_resolved: boolean, '
                    'agent_comment: string>>'
                ),
            ),
        ],
        name='customers',
    )
    expected = ibis.Schema.from_tuples(
        [
            ('cid', dt.int64),
            ('mktsegment', dt.string),
            (
                'address',
                dt.Struct.from_tuples(
                    [
                        ('city', dt.string),
                        ('street', dt.string),
                        ('street_number', dt.int32),
                        ('zip', dt.int16),
                    ]
                ),
            ),
            ('phone_numbers', dt.Array(dt.string)),
            (
                'orders',
                dt.Array(
                    dt.Struct.from_tuples(
                        [
                            ('oid', dt.int64),
                            ('status', dt.string),
                            ('totalprice', dt.Decimal(12, 2)),
                            ('order_date', dt.string),
                            (
                                'items',
                                dt.Array(
                                    dt.Struct.from_tuples(
                                        [
                                            ('iid', dt.int64),
                                            ('name', dt.string),
                                            ('price', dt.Decimal(12, 2)),
                                            (
                                                'discount_perc',
                                                dt.Decimal(12, 2),
                                            ),
                                            ('shipdate', dt.string),
                                        ]
                                    )
                                ),
                            ),
                        ]
                    )
                ),
            ),
            (
                'web_visits',
                dt.Map(
                    dt.string,
                    dt.Struct.from_tuples(
                        [
                            ('user_agent', dt.string),
                            ('client_ip', dt.string),
                            ('visit_date', dt.string),
                            ('duration_ms', dt.int32),
                        ]
                    ),
                ),
            ),
            (
                'support_calls',
                dt.Array(
                    dt.Struct.from_tuples(
                        [
                            ('agent_id', dt.int64),
                            ('call_date', dt.string),
                            ('duration_ms', dt.int64),
                            ('issue_resolved', dt.boolean),
                            ('agent_comment', dt.string),
                        ]
                    )
                ),
            ),
        ]
    )
    assert customers.schema() == expected


def test_schema_subset():
    s1 = ibis.schema([('a', dt.int64), ('b', dt.int32), ('c', dt.string)])

    s2 = ibis.schema([('a', dt.int64), ('c', dt.string)])

    assert s1 > s2
    assert s2 < s1

    assert s1 >= s2
    assert s2 <= s1


def test_empty_schema():
    schema = ibis.schema([])
    result = repr(schema)
    expected = """\
ibis.Schema {
}"""
    assert result == expected


def test_nullable_output():
    sch = ibis.schema(
        [
            ('foo', 'int64'),
            ('bar', ibis.expr.datatypes.int64(nullable=False)),
            ('baz', 'boolean'),
        ]
    )

    sch_str = str(sch)
    assert 'foo  int64' in sch_str
    assert 'foo  int64[non-nullable]' not in sch_str
    assert 'bar  int64[non-nullable]' in sch_str
    assert 'baz  boolean' in sch_str
    assert 'baz  boolean[non-nullable]' not in sch_str


@pytest.fixture
def df():
    return pd.DataFrame({"A": pd.Series([1], dtype="int8"), "b": ["x"]})


def test_apply_to_column_rename(df):
    schema = ibis.schema([("a", "int8"), ("B", "string")])
    expected = df.rename({"A": "a", "b": "B"}, axis=1)
    tm.assert_frame_equal(schema.apply_to(df.copy()), expected)


def test_apply_to_column_order(df):
    schema = ibis.schema([("a", "int8"), ("b", "string")])
    expected = df.rename({"A": "a"}, axis=1)
    new_df = schema.apply_to(df.copy())
    tm.assert_frame_equal(new_df, expected)
