"""This module provides the interface for a DTA record file."""
import logging

from datetime import date, datetime
from decimal import Decimal
from itertools import count
from typing import Tuple, Union

from dta.constants import ChargesRule, IdentificationBankAddress, IdentificationPurpose
from dta.records import DTARecord836
from dta.records.record import DTARecord
from dta.records.record890 import DTARecord890


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s\n%(message)s')
LOGGER = logging.getLogger(f'{__name__}-validation')


class DTAFile(object):
    """DTA File holding records

    Implementation of a DTA File holding a list of TA records.

    While record instances can be added using the ``add_record`` method,
    it is recommended to use the ``add_<transaction_type>_record``
    (so far only ``836``) method instead.
    """

    def __init__(self, sender_id, client_clearing, creation_date=None):
        """

        Args:
            sender_id: Data file sender
            identification (5 characters exactly)
            client_clearing: Bank clearing
            no. of the ordering party's bank
            creation_date: Date when data file was created.
        """
        self.records: [DTARecord] = []
        self.sender_id = sender_id
        self.client_clearing = client_clearing
        self.creation_date = creation_date if creation_date is not None else datetime.now()

    def add_record(self, record: DTARecord):
        """Add a new record to the file.

        Args:
            record: The record to add

        Raises:
            ValueError: When trying to add a TA 890 record.
        """
        if record.header.transaction_type == 890:
            raise ValueError('Adding invalid record:'
                             ' TA 890 record is generated automatically and should not be added.')
        record.header.sender_id = self.sender_id
        record.header.client_clearing = self.client_clearing
        record.header.creation_date = self.creation_date
        self.records.append(record)

    def validate(self):
        """Validate the all records in the file.

        Returns: ``False`` if there are format errors, no
        records or any other reason which will prevent the
        file from being processed; ``True`` otherwise.
        """
        if not self.records:
            return False

        valid_file = True

        creation_date = self.records[0].header.creation_date
        sender_id = self.records[0].header.sender_id

        for i, record in enumerate(self.records):
            sequence_nr = str(i + 1)
            if record.header.sequence_nr.strip().lstrip('0') != sequence_nr:
                record.header.add_error(
                    'sequence_nr',
                    f"SEQUENCE ERROR: Must be consecutive commencing with 1 in ascending order."
                    f" (expected {sequence_nr}, got {record.header.sequence_nr})"
                )
                valid_file = False

            if record.header.creation_date != creation_date:
                record.header.add_error(
                    'creation_date',
                    'DIFFERENT: Must be identical with the creation date on the first record of the data file.')
                valid_file = False

            if record.header.sender_id != sender_id:
                record.header.add_error('sender_id',
                                        "DIFFERENT: Must be identical with the first record on the data carrier.")
                valid_file = False

            record.validate()

        return valid_file

    def add_836_record(self,  # pylint: disable=too-many-arguments,too-many-locals
                       reference: str,
                       client_account: str,
                       processing_date: date,
                       currency: str,
                       amount: Decimal,
                       client_address: Tuple[str, str, str],
                       recipient_iban: str,
                       recipient_name: str,
                       recipient_address: Tuple[str, str],
                       identification_purpose: IdentificationPurpose,
                       purpose: Union[Tuple[str, str, str], str],
                       charges_rules: ChargesRule,
                       bank_address_type: IdentificationBankAddress = IdentificationBankAddress.BENEFICIARY_ADDRESS,
                       bank_address: Tuple[str, str] = ('', ''),
                       conversation_rate: Decimal = None):
        """Add a new TA 836 record.

        Args:
            reference: transaction no. defined by the ordering
                party; must be unique within a data file.
            client_account: Account to be debited (Only IBAN
                is accepted, despite the fact that the
                standard accepts both with or without IBAN)
            processing_date: The date at which
                the payment should be processed
            currency: The currency for the amount of the payment
            amount: The actual amount of the payment
            client_address: Ordering party's address
                (3 times 35 characters)
            recipient_iban: The beneficiary's IBAN
            recipient_name: Name of the beneficiary
            recipient_address: Address of the beneficiary
                (2 times 35 characters)
            identification_purpose: Identification of purpose,
                use ``IdentificationPurpose`` for the values.
            purpose: Purpose of the payment
                Structured reference number:
                    1 line of 20 positions fixed (without
                    blanks), commencing with 2-digit check-digit
                    (PP) as a string or a tuple where only
                    the first value will be considered.
                Unstructured, free text:
                    3 lines of 35 characters as a tuple
            charges_rules: Rules for charges,
                use ``ChargesRule`` for the values
            bank_address_type: Identification bank address, use
                ``IdentificationBankAddress`` for the values.
            bank_address: Beneficiary's institution
                When option ``IdentificationBankAddress.BIC_ADDRESS`` or
                ``IdentificationBankAddress.SWIFTH_ADDRESS`` (``'A'``):
                    8- or 11-digit BIC address (=SWIFT address) as a
                    string or a tuple where  only the first value will
                    be considered.
            When option
            ``IdentificationBankAddress.BENEFICIARY_ADDRESS``:
                Name and address of the beneficiary's institution If
                ``recipient_iban`` contains a CH or LI IBAN, no details
                on the financial institution are required. In this case,
                the values of the parameters ``bank_address_type`` and
                ``bank_address`` are ignored and set automatically.
            conversation_rate: Only indicated if previously agreed
                on the basis of the bank's foreign exchange rate.
                A maximum of 6 decimal places is permitted.
        """
        record = DTARecord836()
        record.reference = reference
        record.client_account = client_account
        record.value_date = processing_date
        record.currency = currency
        record.amount = amount
        record.conversation_rate = conversation_rate
        record.client_address = client_address
        if recipient_iban[:2] in ('CH', 'LI'):
            record.bank_address_type = IdentificationBankAddress.BENEFICIARY_ADDRESS
            record.bank_address = ('', '')
        else:
            record.bank_address_type = bank_address_type
            record.bank_address = bank_address
        record.recipient_iban = recipient_iban
        record.recipient_name = recipient_name
        record.recipient_address = recipient_address
        record.identification_purpose = identification_purpose
        record.purpose = purpose
        record.charges_rules = charges_rules

        self.add_record(record)

    def generate(self) -> bytes:
        self.records.sort(key=lambda record: (
            record.header.processing_date if record.header.transaction_type in ('826', '827') else record.value_date,
            record.header.sender_id,
            record.header.client_clearing
        ))

        sequence_nr = count(start=1, step=1)
        for record in self.records:
            record.header.sequence_nr = next(sequence_nr)

        if not self.validate():
            logger.error('The file contains (a) format error(s) and cannot be processed.')
            for record in self.records:
                if record.has_errors():
                    logger.error('TA %s record (seq no %s, ref: %s) not processed, reason:\n  %s',
                                 record.header.transaction_type,
                                 record.header.sequence_nr,
                                 record.reference,
                                 '\n  '.join(record.validation_errors))
                else:
                    logger.error('TA %s record (seq no %s, ref: %s) not processed, reason:\n'
                                 '  Record is valid but the file has a format error')
            return ''.encode('latin-1')

        valid_records = [record for record in self.records if not record.has_errors()]
        invalid_records = tuple(record for record in self.records if record.has_errors())

        for invalid_record in invalid_records:
            logger.error('TA %s record (seq no %s, ref: %s) not processed, reason:\n  %s',
                         invalid_record.header.transaction_type,
                         invalid_record.header.sequence_nr,
                         invalid_record.reference,
                         '\n  '.join(invalid_record.validation_errors))

        if not valid_records:
            logger.error('No valid records, file not generated')
            return ''.encode('latin-1')

        for valid_record in valid_records:
            if valid_record.has_warnings():
                logger.warning('TA %s record (seq no %s, ref: %s) was processed '
                               'but triggered the following warning(s):\n  %s',
                               valid_record.header.transaction_type,
                               valid_record.header.sequence_nr,
                               valid_record.reference,
                               '\n  '.join(valid_record.validation_warnings))

        sequence_nr = count(start=1, step=1)
        for record in valid_records:
            record.header.sequence_nr = next(sequence_nr)
        total_record = self.generate_890_record(valid_records)
        total_record.validate()  # just to make sure

        if total_record.has_errors():
            errors = '\n - '.join(('', self.records[-1].field_errors))
            raise RuntimeError(f'Unexpected error in TA 890 total record:{errors}')

        valid_records.append(total_record)

        return '\r\n'.join(record.generate() for record in valid_records).encode('latin-1')
