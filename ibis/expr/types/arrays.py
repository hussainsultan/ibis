from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

from public import public

from .generic import AnyColumn, AnyScalar, AnyValue, ColumnExpr, literal
from .typing import V

if TYPE_CHECKING:
    import ibis.expr.datatypes as dt
    import ibis.expr.types as ir

import ibis.common.exceptions as com


@public
class ArrayValue(AnyValue):
    def length(self) -> ir.IntegerValue:
        """Compute the length of an array.

        Returns
        -------
        IntegerValue
            The integer length of `self`

        Examples
        --------
        >>> import ibis
        >>> a = ibis.array([1, 2, 3])
        >>> a.length()
        int64 = ArrayLength
          value: array<int8> = [1, 2, 3]
        """
        import ibis.expr.operations as ops

        return ops.ArrayLength(self).to_expr()

    def __getitem__(
        self,
        index: int | ir.IntegerValue | slice,
    ) -> ir.ValueExpr:
        """Extract one or more elements of `self`.

        Parameters
        ----------
        index
            Index into `array`

        Returns
        -------
        ValueExpr
            - If `index` is an [`int`][int] or
              [`IntegerValue`][ibis.expr.types.IntegerValue] then the return
              type is the element type of `self`.
            - If `index` is a [`slice`][slice] then the return type is the same
              type as the input.

        Examples
        --------
        Extract a single element

        >>> import ibis
        >>> x = ibis.array([1, 2, 3, 4])
        >>> x[2]
        int8 = ArrayIndex
          value: array<int8> = [1, 2, 3, 4]
          index:
            value: int8 = 2

        Extract a range of elements

        >>> import ibis
        >>> x = ibis.array([1, 2, 3, 4])
        >>> x[1:3]
        array<int8> = ArraySlice
          value: array<int8> = [1, 2, 3, 4]
          start:
            value: int8 = 1
          stop:
            value: int8 = 3
        """
        import ibis.expr.operations as ops

        if isinstance(index, slice):
            start = index.start
            stop = index.stop
            step = index.step

            if step is not None and step != 1:
                raise NotImplementedError('step can only be 1')

            op = ops.ArraySlice(self, start if start is not None else 0, stop)
        else:
            op = ops.ArrayIndex(self, index)
        return op.to_expr()

    def __add__(self, other: ArrayValue) -> ArrayValue:
        """Concatenate this array with another.

        Parameters
        ----------
        other
            Array to concat with `self`

        Returns
        -------
        ArrayValue
            `self` concatenated with `other`

        Examples
        --------
        >>> import ibis
        >>> a = ibis.array([1, 2])
        >>> b = ibis.array([3, 4, 5])
        >>> a + b
        array<int8> = ArrayConcat
          left:
            value: array<int8> = [1, 2]
          right:
            value: array<int8> = [3, 4, 5]
        """
        import ibis.expr.operations as ops

        return ops.ArrayConcat(self, other).to_expr()

    def __radd__(self, other: ArrayValue) -> ArrayValue:
        """Concatenate this array with another.

        Parameters
        ----------
        other
            Array to concat with `self`

        Returns
        -------
        ArrayValue
            `self` concatenated with `other`

        Examples
        --------
        >>> import ibis
        >>> a = ibis.array([1, 2])
        >>> b = ibis.array([3, 4, 5])
        >>> b + a
        array<int8> = ArrayConcat
          left:
            value: array<int8> = [3, 4, 5]
          right:
            value: array<int8> = [1, 2]
        """
        import ibis.expr.operations as ops

        return ops.ArrayConcat(self, other).to_expr()

    def __mul__(self, n: int | ir.IntegerValue) -> ArrayValue:
        """Repeat this array `n` times.

        Parameters
        ----------
        n
            Number of times to repeat `self`.

        Returns
        -------
        ArrayValue
            `self` repeated `n` times

        Examples
        --------
        >>> import ibis
        >>> x = ibis.array([1, 2])
        >>> x * 2
        array<int8> = ArrayRepeat
          value: array<int8> = [1, 2]
          times:
            value: int8 = 2
        """
        import ibis.expr.operations as ops

        return ops.ArrayRepeat(self, n).to_expr()

    def __rmul__(self, n: int | ir.IntegerValue) -> ArrayValue:
        """Repeat this array `n` times.

        Parameters
        ----------
        n
            Number of times to repeat `self`.

        Returns
        -------
        ArrayValue
            `self` repeated `n` times

        Examples
        --------
        >>> import ibis
        >>> x = ibis.array([1, 2])
        >>> 2 * x
        array<int8> = ArrayRepeat
          value: array<int8> = [1, 2]
          times:
            value: int8 = 2
        """
        import ibis.expr.operations as ops

        return ops.ArrayRepeat(self, n).to_expr()


@public
class ArrayScalar(AnyScalar, ArrayValue):
    pass


@public
class ArrayColumn(AnyColumn, ArrayValue):
    pass


@public
def array(
    values: Iterable[V],
    type: str | dt.DataType | None = None,
) -> ArrayValue:
    """Create an array expression.

    If the input expressions are all column expressions, then the output will
    be an `ArrayColumn`. The input columns will be concatenated row-wise to
    produce each array in the output array column. Each array will have length
    _n_, where _n_ is the number of input columns. All input columns should be
    of the same datatype.

    If the input expressions are Python literals, then the output will be a
    single `ArrayScalar` of length _n_, where _n_ is the number of input
    values. This is equivalent to

    ```python
    values = [1, 2, 3]
    ibis.literal(values)
    ```

    Parameters
    ----------
    values
        An iterable of Ibis expressions or a list of Python literals
    type
        An instance of `ibis.expr.datatypes.DataType` or a string indicating
        the ibis type of `value`.

    Returns
    -------
    ArrayValue
        An array column (if the inputs are column expressions), or an array
        scalar (if the inputs are Python literals)

    Examples
    --------
    Create an array column from column expressions
    >>> import ibis
    >>> t = ibis.table([('a', 'int64'), ('b', 'int64')], name='t')
    >>> result = ibis.array([t.a, t.b])

    Create an array scalar from Python literals
    >>> import ibis
    >>> result = ibis.array([1.0, 2.0, 3.0])
    """
    import ibis.expr.operations as ops

    if all([isinstance(value, ColumnExpr) for value in values]):
        return ops.ArrayColumn(values).to_expr()
    elif any([isinstance(value, ColumnExpr) for value in values]):
        raise com.IbisTypeError(
            'To create an array column using `array`, all input values must '
            'be column expressions.'
        )
    else:
        try:
            return literal(list(values), type=type)
        except com.IbisTypeError as e:
            raise com.IbisTypeError(
                'Could not create an array scalar from the values provided '
                'to `array`. Ensure that all input values have the same '
                'Python type, or can be casted to a single Python type.'
            ) from e
