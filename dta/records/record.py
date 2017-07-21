from itertools import chain

from dta.records.common import FieldsValidationMixin
from dta.records.header import DTAHeader


class DTARecord(FieldsValidationMixin):
    def __init__(self, processing_date, recipient_clearing, creation_date, client_clearing, sender_id, sequence_nr):
        super().__init__()
        self.header = DTAHeader(processing_date, recipient_clearing, creation_date, client_clearing, sender_id,
                                sequence_nr)

    def validate(self):
        self.header.validate()

