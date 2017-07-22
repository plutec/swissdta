from itertools import chain

from dta.records.common import ValidationHandler
from dta.records.header import DTAHeader


class DTARecord(ValidationHandler):
    def __init__(self):
        super().__init__()
        self.header = DTAHeader()

    def validate(self):
        self.header.validate()

    def has_errors(self):
        return self.header.has_errors() or super().has_errors()
