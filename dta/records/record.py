from itertools import chain

from dta.records.common import FieldsValidationMixin
from dta.records.header import DTAHeader


class DTARecord(FieldsValidationMixin):
    def __init__(self):
        super().__init__()
        self.header = DTAHeader()

    def validate(self):
        self.header.validate()

    def has_errors(self):
        return self.header.has_errors() or super().has_errors()
