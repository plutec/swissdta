from datetime import date, datetime
from decimal import Decimal
from itertools import count

from dta.constants import ChargesRule, IdentificationBankAddress, IdentificationPurpose
from dta.records import DTARecord836
from dta.records.record import DTARecord
from dta.records.record890 import DTARecord890


class DTAFile(object):

    def __init__(self, sender_id, client_clearing, creation_date=None):
        self.records: [DTARecord] = []
        self.sender_id = sender_id
        self.client_clearing = client_clearing
        self.creation_date = creation_date if creation_date is not None else datetime.now()

    def add_record(self, record: DTARecord):
        if record.header.transaction_type == 890:
            raise ValueError('Adding invalid record:'
                             ' TA 890 record is generated automatically and should not be added.')
        record.header.sender_id = self.sender_id
        record.header.client_clearing = self.client_clearing
        record.header.creation_date = self.creation_date
        self.records.append(record)

    def validate(self):
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

    def generate_890_record(self, records):
        record = DTARecord890()
        record.header.sequence_nr = len(records) + 1
        record.header.sender_id = self.sender_id
        record.header.creation_date = self.creation_date
        record.amount = sum(Decimal(record.amount.strip().replace(',', '.')) for record in records)
        return record

    def add_836_record(self,
                       reference: str,
                       client_account: str,
                       processing_date: date,
                       currency: str,
                       amount: Decimal,
                       client_address: (str, str, str),
                       recipient_iban: str,
                       recipient_name: str,
                       recipient_address: (str, str),
                       identification_purpose: IdentificationPurpose,
                       purpose: (str, str, str),
                       charges_rules: ChargesRule,
                       bank_address_type: IdentificationBankAddress = IdentificationBankAddress.BENEFICIARY_ADDRESS,
                       bank_address: (str, str) = ('', ''),
                       conversation_rate: Decimal = None,):
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
            return ''.encode('latin-1')

        valid_records = [record for record in self.records if not record.has_errors()]
        invalid_records = ((record for record in self.records if record.has_errors()),)

        if not valid_records:
            return ''.encode('latin-1')

        sequence_nr = count(start=1, step=1)
        for record in valid_records:
            record.header.sequence_nr = next(sequence_nr)
        total_record = self.generate_890_record(valid_records)
        total_record.validate()

        if total_record.has_errors():
            errors = '\n - '.join(('', self.records[-1].field_errors))
            raise RuntimeError(f'Unexpected error in TA 890 total record:{errors}')

        valid_records.append(total_record)

        return '\r\n'.join(record.generate() for record in valid_records).encode('latin-1')
