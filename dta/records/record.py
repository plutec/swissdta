from itertools import chain

from dta.records.common import FieldsValidationMixin
from dta.records.header import DTAHeader


class DTARecord(FieldsValidationMixin):
    def __init__(self):
        super().__init__()
        self.header = DTAHeader()

    def validate(self):
        self.header.validate()

