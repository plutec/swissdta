"""Tests for the base field"""

import pytest

from dta.constants import FillSide
from dta.fields import Field
from dta.records.record import DTARecord


@pytest.mark.parametrize(('input_value', 'expected_value', 'field_params'), (
    ('01234', '01234', {'length': 5}),
    ('012345', '012345', {'length': 5}),
    ('0123456789', '0123456789', {'length': 5}),
    ('0123', '0123  ', {'length': 6}),
    ('0123', '0123xx', {'length': 6, 'fillchar': 'x'}),
    ('0123', '0123xx', {'length': 6, 'fillchar': 'x', 'fillside': FillSide.RIGHT}),
    ('0123', '  0123', {'length': 6, 'fillside': FillSide.LEFT}),
    ('0123', 'xx0123', {'length': 6, 'fillchar': 'x', 'fillside': FillSide.LEFT}),
))
def test_padding(input_value, expected_value, field_params):
    """Verify that field values are padded correctly."""
    class TestRecord(DTARecord):
        """Simple Record class for testing"""
        field = Field(**field_params)

    record = TestRecord()
    record.field = input_value
    assert record.field == expected_value


@pytest.mark.parametrize(('value', 'expected_errors', 'field_params'), (
    ('01234', tuple(), {'length': 5}),
    ('012345', ("[field] TOO LONG: '012345' can be at most 5 characters",), {'length': 5}),
    ('0123456789', ("[field] TOO LONG: '0123456789' can be at most 5 characters",), {'length': 5}),
    ('0123', tuple(), {'length': 6})
))
def test_validate(value, expected_errors, field_params):
    """Verify that field values are validated properly"""
    class TestRecord(DTARecord):
        """Simple Record class for testing"""
        field = Field(**field_params)

    record = TestRecord()
    record.field = value
    assert record.validation_warnings == tuple()
    assert record.validation_errors == expected_errors
