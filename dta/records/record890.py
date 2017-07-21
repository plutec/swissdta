from dta.fields import Amount
from .record import DTARecord


class DTARecord890(DTARecord):

    amount = Amount(length=16)

    _fields = ('amount',)
    _template = '01{header}{amount}{padding}'

    def __init__(self, processing_date, recipient_clearing, creation_date, client_clearing, sender_id, sequence_nr,
                 amount):
        super().__init__(processing_date, recipient_clearing, creation_date, client_clearing, sender_id, sequence_nr)
        self.amount = amount

    def generate(self):
        return self._template.format(header=self.header.generate(), amount=self.amount.generate(), padding=' ' * 59)

    def validate(self):
        warnings, record_errors, format_errors = super().validate()

        decimal_places = len(self.amount.strip().split(',', maxsplit=1)[1])
        if decimal_places > 3:
            format_errors.append(
                "[currency] MORE THAN 3 DECIMAL PLACES: Total amount may not contain more than 3 decimal places.")

        return warnings, record_errors, format_errors
