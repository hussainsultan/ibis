from __future__ import annotations

import sqlite3
from datetime import date

import pandas as pd
import pytest
from packaging.version import parse as vparse

import ibis
import ibis.expr.datatypes as dt

# Test with formats 1-7 (with T, Z, and offset modifiers) from:
# https://sqlite.org/lang_datefunc.html#time_values
TIMESTAMPS = [
    "2022-01-02",
    "2022-01-02 03:04",
    "2022-01-02 03:04:05",
    "2022-01-02 03:04:05.678",
    "2022-01-02T03:04",
    "2022-01-02T03:04:05",
    "2022-01-02T03:04:05.678",
    None,
]
TIMESTAMPS_TZ = [
    "2022-01-02 03:04Z",
    "2022-01-02 03:04:05Z",
    "2022-01-02 03:04:05.678Z",
    "2022-01-02 03:04+01:00",
    "2022-01-02 03:04:05+01:00",
    "2022-01-02 03:04:05.678+01:00",
    None,
]


@pytest.fixture(scope="session")
def db(tmp_path_factory):
    path = str(tmp_path_factory.mktemp("databases") / "formats.db")
    con = sqlite3.connect(path)
    try:
        with con:
            con.execute("CREATE TABLE timestamps (ts TIMESTAMP)")
            con.execute("CREATE TABLE timestamps_tz (ts TIMESTAMPTZ)")
            con.execute("CREATE TABLE weird (str_col STRING, date_col ITSADATE)")
            con.execute("CREATE TABLE basic (a INTEGER, b REAL, c BOOLEAN, d BLOB)")
            con.executemany(
                "INSERT INTO timestamps VALUES (?)", [(t,) for t in TIMESTAMPS]
            )
            con.executemany(
                "INSERT INTO timestamps_tz VALUES (?)", [(t,) for t in TIMESTAMPS_TZ]
            )
            con.executemany(
                "INSERT INTO weird VALUES (?, ?)",
                [
                    ("a", "2022-01-01"),
                    ("b", "2022-01-02"),
                    ("c", "2022-01-03"),
                    ("d", "2022-01-04"),
                ],
            )
    finally:
        con.close()
    return path


@pytest.mark.parametrize(
    "table, data",
    [("timestamps", TIMESTAMPS), ("timestamps_tz", TIMESTAMPS_TZ)],
)
def test_timestamps(db, table, data):
    con = ibis.sqlite.connect(db)
    t = con.table(table)
    assert t.ts.type().is_timestamp()
    res = t.ts.execute()
    # the "mixed" format was added in pandas 2.0.0
    format = "mixed" if vparse(pd.__version__) >= vparse("2.0.0") else None
    stamps = pd.to_datetime(data, format=format, utc=True)
    if t.ts.type().timezone is None:
        # we're casting to timestamp without a timezone, so remove it in the
        # expected output
        stamps = stamps.tz_localize(None)
    sol = pd.Series(stamps)
    assert res.equals(sol)


def test_type_map(db):
    con = ibis.sqlite.connect(db, type_map={"STRING": dt.string, "ITSADATE": "date"})
    t = con.table("weird")
    expected_schema = ibis.schema({"str_col": "string", "date_col": "date"})
    assert t.schema() == expected_schema
    res = t.filter(t.str_col == "a").execute()
    sol = pd.DataFrame(
        {"str_col": ["a"], "date_col": pd.Series([date(2022, 1, 1)], dtype="object")}
    )
    sol["date_col"] = sol["date_col"].astype(res["date_col"].dtype)

    assert res.equals(sol)


def test_read_basic_types(db):
    con = ibis.sqlite.connect(db)
    t = con.table("basic")
    assert t.schema() == ibis.schema(
        {"a": "int64", "b": "float64", "c": "bool", "d": "binary"}
    )
