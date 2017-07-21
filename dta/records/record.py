from dta import fields

from dta.records.common import FieldsValidationMixin
from dta.records.header import DTAHeader


class DTARecord(FieldsValidationMixin):

        for name, field in cls._fields.items():
            field.name = name
            setattr(self, name, field.default)

    def __init__(self, processing_date, recipient_clearing, creation_date, client_clearing, sender_id, sequence_nr):
        super().__init__()
        self.header = DTAHeader(processing_date, recipient_clearing, creation_date, client_clearing, sender_id,
                                sequence_nr)

    def check(self):
        for name, field in self._fields.items():
            if field.required and not getattr(self, name).strip():
                raise DTAValueError('Field %s is required' % field.name)

    def generate(self):
        self.check()

    def _gen_segment(self, items, length=128):
        segment = ''.join(items)
        assert len(segment) == length
        return segment

    def _generate(self, segments):
        return '\r\n'.join(segments)


class DTAValueError(Exception):
    pass
