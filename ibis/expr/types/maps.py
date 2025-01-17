from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, Mapping

from public import public

from .generic import AnyColumn, AnyScalar, AnyValue, literal
from .typing import K, V

if TYPE_CHECKING:
    import ibis.expr.datatypes as dt
    import ibis.expr.types as ir


@public
class MapValue(AnyValue):
    def get(
        self,
        key: ir.ValueExpr,
        default: ir.ValueExpr | None = None,
    ) -> ir.ValueExpr:
        """Return the value for `key` from `expr` or the default if `key` is not in the map.

        Parameters
        ----------
        key
            Expression to use for key
        default
            Expression to return if `key` is not a key in `expr`

        Returns
        -------
        ValueExpr
            The element type of `self`

        Examples
        --------
        >>> import ibis
        >>> m = ibis.map({"a": 1, "b": 2})
        >>> m.get("a")
        int8 = MapValueOrDefaultForKey
          value: map<string, int8> = {'a': 1, 'b': 2}
          key:
            value: string = 'a'
          default:
            value: null = None
        >>> m.get("c", 3)
        int8 = MapValueOrDefaultForKey
          value: map<string, int8> = {'a': 1, 'b': 2}
          key:
            value: string = 'c'
          default:
            value: int8 = 3
        >>> m.get("d")
        int8 = MapValueOrDefaultForKey
          value: map<string, int8> = {'a': 1, 'b': 2}
          key:
            value: string = 'd'
          default:
            value: null = None
        """  # noqa: E501
        import ibis.expr.operations as ops

        return ops.MapValueOrDefaultForKey(self, key, default).to_expr()

    def length(self) -> ir.IntegerValue:
        """Return the number of key-value pairs in the map.

        Returns
        -------
        IntegerValue
            The number of elements in `self`

        Examples
        --------
        >>> import ibis
        >>> m = ibis.map({"a": 1, "b": 2})
        >>> m.length()
        int64 = MapLength
          value: map<string, int8> = {'a': 1, 'b': 2}
        """
        import ibis.expr.operations as ops

        return ops.MapLength(self).to_expr()

    def __getitem__(self, key: ir.ValueExpr) -> ir.ValueExpr:
        """Get the value for a given map `key`.

        !!! info "This operation may have different semantics depending on the backend."

            Some backends return `NULL` when a key is missing, others may fail
            the query.

        Parameters
        ----------
        key
            A map key

        Returns
        -------
        ValueExpr
            An element with the value type of the map

        Examples
        --------
        >>> import ibis
        >>> m = ibis.map({"a": 1, "b": 2})
        >>> m["a"]
        int8 = MapValueForKey
          value: map<string, int8> = {'a': 1, 'b': 2}
          key:
            value: string = 'a'
        >>> m["c"]  # note that this does not fail on construction
        int8 = MapValueForKey
          value: map<string, int8> = {'a': 1, 'b': 2}
          key:
            value: string = 'c'
        """  # noqa: E501
        import ibis.expr.operations as ops

        return ops.MapValueForKey(self, key).to_expr()

    def keys(self) -> ir.ArrayValue:
        """Extract the keys of a map.

        Returns
        -------
        ArrayValue
            The keys of `self`

        Examples
        --------
        >>> import ibis
        >>> m = ibis.map({"a": 1, "b": 2})
        >>> m.keys()
        array<string> = MapKeys
          value: map<string, int8> = {'a': 1, 'b': 2}
        """
        import ibis.expr.operations as ops

        return ops.MapKeys(self).to_expr()

    def values(self) -> ir.ArrayValue:
        """Extract the values of a map.

        Returns
        -------
        ArrayValue
            The values of `self`

        Examples
        --------
        >>> import ibis
        >>> m = ibis.map({"a": 1, "b": 2})
        >>> m.keys()
        array<int8> = MapValues
          value: map<string, int8> = {'a': 1, 'b': 2}
        """
        import ibis.expr.operations as ops

        return ops.MapValues(self).to_expr()

    def __add__(self, other: MapValue) -> MapValue:
        """Concatenate this map with another.

        Parameters
        ----------
        other
            Map to concatenate with `self`

        Returns
        -------
        MapValue
            `self` concatenated with `other`

        Examples
        --------
        >>> import ibis
        >>> m1 = ibis.map({"a": 1, "b": 2})
        >>> m2 = ibis.map({"c": 3, "d": 4})
        >>> m1 + m2
        map<string, int8> = MapConcat
          left:
            value: map<string, int8> = {'a': 1, 'b': 2}
          right:
            value: map<string, int8> = {'c': 3, 'd': 4}
        """
        import ibis.expr.operations as ops

        return ops.MapConcat(self, other).to_expr()

    def __radd__(self, other: MapValue) -> MapValue:
        """Concatenate this map with another.

        Parameters
        ----------
        other
            Map to concatenate with `self`

        Returns
        -------
        MapValue
            `self` concatenated with `other`

        Examples
        --------
        >>> import ibis
        >>> m1 = ibis.map({"a": 1, "b": 2})
        >>> m2 = ibis.map({"c": 3, "d": 4})
        >>> m1 + m2
        map<string, int8> = MapConcat
          left:
            value: map<string, int8> = {'a': 1, 'b': 2}
          right:
            value: map<string, int8> = {'c': 3, 'd': 4}
        """
        import ibis.expr.operations as ops

        return ops.MapConcat(self, other).to_expr()


@public
class MapScalar(AnyScalar, MapValue):
    pass  # noqa: E701,E302


@public
class MapColumn(AnyColumn, MapValue):
    pass  # noqa: E701,E302


@public
def map(
    value: Iterable[tuple[K, V]] | Mapping[K, V],
    type: str | dt.DataType | None = None,
) -> MapValue:
    """Create a map literal from a [`dict`][dict] or other mapping.

    Parameters
    ----------
    value
        the literal map value
    type
        An instance of `ibis.expr.datatypes.DataType` or a string indicating
        the ibis type of `value`.

    Returns
    -------
    MapScalar
        An expression representing a literal map (associative array with
        key/value pairs of fixed types)

    Examples
    --------
    Create a map literal from a dict with the type inferred
    >>> import ibis
    >>> t = ibis.map(dict(a=1, b=2))

    Create a map literal from a dict with the specified type
    >>> import ibis
    >>> t = ibis.map(dict(a=1, b=2), type='map<string, double>')
    """
    return literal(dict(value), type=type)
