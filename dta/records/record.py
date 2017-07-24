"""Base class for DTA TA records"""

from itertools import chain

from dta.records.common import ValidationHandler
from dta.records.header import DTAHeader


class DTARecord(ValidationHandler):
    """Base class for DTA TA records.

    This class should not be instantiated directly but subclassed
    instead. It automatically generates a empty header required for all
    types of records.

    The constructor (of this class and its children) should not accept
    record values. All fields should be set after initialization and
    all field attributes should use a subclass of `dta.fields.Field`.
    """
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
        """Triggers the validation of the record.

        This validate the data in the record according to the
        validation defined in the `DTA Standards and Formats`_.

        .. _DTA Standards and Formats: https://www.six-interbank-clearing.com/dam/downloads/en/standardization/dta/dta.pdf
        """
        self.header.validate()
