from dta.fields import Amount
from dta.records.record import DTARecord


class DTARecord890(DTARecord):

    amount = Amount(length=16)

    _fields = ('amount',)
    _template = '01{header}{amount}{padding}\r\n'

    def __init__(self):
        super().__init__()
        self.header.transaction_type = 890

    def generate(self):
        return self._template.format(header=self.header.generate(), amount=self.amount, padding=' ' * 59)

    def validate(self):
        super().validate()

        if self.header.transaction_type != '890':
            self.header.add_error('transaction_type', "INVALID: Transaction type must be TA 890.")

        if self.header.client_clearing.strip():
            self.header.add_error('client_clearing', 'INVALID: must be completed with blanks')

        decimal_places = len(self.amount.strip().split(',', maxsplit=1)[1])
        if decimal_places > 3:
            self.add_error('currency',
                           "MORE THAN 3 DECIMAL PLACES: Total amount may not contain more than 3 decimal places.")
