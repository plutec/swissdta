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

