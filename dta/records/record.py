from itertools import chain

from dta.records.common import ValidationHandler
from dta.records.header import DTAHeader


class DTARecord(ValidationHandler):
    def __init__(self):
        super().__init__()
        self.header = DTAHeader()

    @property
    def validation_warnings(self):
        return tuple(warning for warning in chain(self.header.validation_warnings, super().validation_warnings))

    @property
    def validation_errors(self):
        return tuple(error for error in chain(self.header.validation_errors, super().validation_errors))

    def has_warnings(self):
        return self.header.has_warnings() or super().has_warnings()

    def has_errors(self):
        return self.header.has_errors() or super().has_errors()

    def validate(self):
        self.header.validate()
