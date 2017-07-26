"""Tests for the DTA file"""
from datetime import date
from decimal import Decimal

import pytest

from dta.constants import IdentificationPurpose, ChargesRule
from dta.dta import DTAFile


@pytest.mark.parametrize(('record_data', 'duplicate_record_indexes'), (
    ([{
        'reference': '01234567890',
        'client_account': 'CH38 0888 8123 4567 8901 2',
        'processing_date': date(2017, 7, 24),
        'currency': 'CHF',
        'amount': Decimal(10),
        'client_address': ('Alphabet Inc', 'Brandschenkestrasse 110', '8002 Zürich'),
        'recipient_iban': 'CH9300762011623852957',
        'recipient_name': 'Herr Peter Haller',
        'recipient_address': ('Marktplaz 4', '9400 Rorschach'),
        'identification_purpose': IdentificationPurpose.UNSTRUCTURED,
        'purpose': ('Reference Uniqueness Test', '', ''),
        'charges_rules': ChargesRule.OUR
    }, {
        'reference': '01234567890',
        'client_account': 'CH38 0888 8123 4567 8901 2',
        'processing_date': date(2017, 7, 24),
        'currency': 'CHF',
        'amount': Decimal(10),
        'client_address': ('Alphabet Inc', 'Brandschenkestrasse 110', '8002 Zürich'),
        'recipient_iban': 'CH9300762011623852957',
        'recipient_name': 'Herr Peter Haller',
        'recipient_address': ('Marktplaz 4', '9400 Rorschach'),
        'identification_purpose': IdentificationPurpose.UNSTRUCTURED,
        'purpose': ('Reference Uniqueness Test', '', ''),
        'charges_rules': ChargesRule.OUR
    }], (0, 1)),
    ([{
        'reference': '01234567890',
        'client_account': 'CH38 0888 8123 4567 8901 2',
        'processing_date': date(2017, 7, 24),
        'currency': 'CHF',
        'amount': Decimal(10),
        'client_address': ('Alphabet Inc', 'Brandschenkestrasse 110', '8002 Zürich'),
        'recipient_iban': 'CH9300762011623852957',
        'recipient_name': 'Herr Peter Haller',
        'recipient_address': ('Marktplaz 4', '9400 Rorschach'),
        'identification_purpose': IdentificationPurpose.UNSTRUCTURED,
        'purpose': ('Reference Uniqueness Test', '', ''),
        'charges_rules': ChargesRule.OUR
    }, {
        'reference': '01234567890',
        'client_account': 'CH38 0888 8123 4567 8901 2',
        'processing_date': date(2017, 7, 24),
        'currency': 'CHF',
        'amount': Decimal(10),
        'client_address': ('Alphabet Inc', 'Brandschenkestrasse 110', '8002 Zürich'),
        'recipient_iban': 'CH9300762011623852957',
        'recipient_name': 'Herr Peter Haller',
        'recipient_address': ('Marktplaz 4', '9400 Rorschach'),
        'identification_purpose': IdentificationPurpose.UNSTRUCTURED,
        'purpose': ('Reference Uniqueness Test', '', ''),
        'charges_rules': ChargesRule.OUR
    }, {
        'reference': '01234567890',
        'client_account': 'CH38 0888 8123 4567 8901 2',
        'processing_date': date(2017, 7, 24),
        'currency': 'CHF',
        'amount': Decimal(10),
        'client_address': ('Alphabet Inc', 'Brandschenkestrasse 110', '8002 Zürich'),
        'recipient_iban': 'CH9300762011623852957',
        'recipient_name': 'Herr Peter Haller',
        'recipient_address': ('Marktplaz 4', '9400 Rorschach'),
        'identification_purpose': IdentificationPurpose.UNSTRUCTURED,
        'purpose': ('Reference Uniqueness Test', '', ''),
        'charges_rules': ChargesRule.OUR
    }, {
        'reference': '01234567890',
        'client_account': 'CH38 0888 8123 4567 8901 2',
        'processing_date': date(2017, 7, 24),
        'currency': 'CHF',
        'amount': Decimal(10),
        'client_address': ('Alphabet Inc', 'Brandschenkestrasse 110', '8002 Zürich'),
        'recipient_iban': 'CH9300762011623852957',
        'recipient_name': 'Herr Peter Haller',
        'recipient_address': ('Marktplaz 4', '9400 Rorschach'),
        'identification_purpose': IdentificationPurpose.UNSTRUCTURED,
        'purpose': ('Reference Uniqueness Test', '', ''),
        'charges_rules': ChargesRule.OUR
    }], (0, 1, 2, 3)),
    ([{
        'reference': '01234567890',
        'client_account': 'CH38 0888 8123 4567 8901 2',
        'processing_date': date(2017, 7, 24),
        'currency': 'CHF',
        'amount': Decimal(10),
        'client_address': ('Alphabet Inc', 'Brandschenkestrasse 110', '8002 Zürich'),
        'recipient_iban': 'CH9300762011623852957',
        'recipient_name': 'Herr Peter Haller',
        'recipient_address': ('Marktplaz 4', '9400 Rorschach'),
        'identification_purpose': IdentificationPurpose.UNSTRUCTURED,
        'purpose': ('Reference Uniqueness Test', '', ''),
        'charges_rules': ChargesRule.OUR
    }, {
        'reference': '01234567890',
        'client_account': 'CH38 0888 8123 4567 8901 2',
        'processing_date': date(2017, 7, 24),
        'currency': 'CHF',
        'amount': Decimal(10),
        'client_address': ('Alphabet Inc', 'Brandschenkestrasse 110', '8002 Zürich'),
        'recipient_iban': 'CH9300762011623852957',
        'recipient_name': 'Herr Peter Haller',
        'recipient_address': ('Marktplaz 4', '9400 Rorschach'),
        'identification_purpose': IdentificationPurpose.UNSTRUCTURED,
        'purpose': ('Reference Uniqueness Test', '', ''),
        'charges_rules': ChargesRule.OUR
    }, {
        'reference': '01234567891',
        'client_account': 'CH38 0888 8123 4567 8901 2',
        'processing_date': date(2017, 7, 24),
        'currency': 'CHF',
        'amount': Decimal(10),
        'client_address': ('Alphabet Inc', 'Brandschenkestrasse 110', '8002 Zürich'),
        'recipient_iban': 'CH9300762011623852957',
        'recipient_name': 'Herr Peter Haller',
        'recipient_address': ('Marktplaz 4', '9400 Rorschach'),
        'identification_purpose': IdentificationPurpose.UNSTRUCTURED,
        'purpose': ('Reference Uniqueness Test', '', ''),
        'charges_rules': ChargesRule.OUR
    }, {
        'reference': '01234567890',
        'client_account': 'CH38 0888 8123 4567 8901 2',
        'processing_date': date(2017, 7, 24),
        'currency': 'CHF',
        'amount': Decimal(10),
        'client_address': ('Alphabet Inc', 'Brandschenkestrasse 110', '8002 Zürich'),
        'recipient_iban': 'CH9300762011623852957',
        'recipient_name': 'Herr Peter Haller',
        'recipient_address': ('Marktplaz 4', '9400 Rorschach'),
        'identification_purpose': IdentificationPurpose.UNSTRUCTURED,
        'purpose': ('Reference Uniqueness Test', '', ''),
        'charges_rules': ChargesRule.OUR
    }], (0, 1, 3))
))
def test_references_uniqueness(record_data, duplicate_record_indexes):
    """Verify the uniqueness of reference numbers within a file."""
    dta_file = DTAFile(sender_id='ABC12', client_clearing='8888')
    for record_datum in record_data:
        dta_file.add_836_record(**record_datum)

    dta_file._sort_records()  # pylint: disable=protected-access
    dta_file._set_sequence_numbers()  # pylint: disable=protected-access
    dta_file.validate()

    for idx in duplicate_record_indexes:
        record = dta_file.records[idx]
        assert (f"[reference] DUPLICATE TRANSACTION NUMBER: reference '{record.reference}' is present more than once."
                in record.validation_errors), f"Reference number '{record.reference}' is not unique within the file."
