from datetime import datetime, timedelta

from dta.constants import FillDirection, PaymentType
from dta.fields import AlphaNumeric, Date, Numeric
from dta.records.common import ValidationHandler


class DTAHeader(ValidationHandler):

    processing_date = Date()
    recipient_clearing = AlphaNumeric(length=12)
    creation_date = Date()
    client_clearing = AlphaNumeric(length=7)
    sender_id = AlphaNumeric(length=5)
    sequence_nr = Numeric(length=5, fillchar='0', filldir=FillDirection.LEFT)
    transaction_type = Numeric(length=3)
    payment_type = Numeric(length=1, value=PaymentType.REGULAR, allowed_values=PaymentType)
    processing_flag = Numeric(length=1, value=0)

    _template = ('{processing_date}{recipient_clearing}00000'
                 '{creation_date}{client_clearing}{sender_id}{sequence_nr}{transaction_type}{payment_type}0')

    def __init__(self) -> None:
        super().__init__()

    def generate(self):
        return self._template.format(
            processing_date=self.processing_date,
            recipient_clearing=self.recipient_clearing,
            creation_date=self.creation_date,
            client_clearing=self.client_clearing,
            sender_id=self.sender_id,
            sequence_nr=self.sequence_nr,
            transaction_type=self.transaction_type,
            payment_type=self.payment_type
        )

    def validate(self):
        now = datetime.now()
        ninety_days_ago = now - timedelta(days=90)
        ninety_days_ahead = now + timedelta(days=90)
        try:
            creation_date = datetime.strptime(self.creation_date, Date.DATE_FORMAT)
        except ValueError:
            self.add_error('creation_date', "INVALID: must contain a valid date.")
        else:
            if not (ninety_days_ago < creation_date < ninety_days_ahead):
                self.add_error('creation_date', "INVALID: creation date may not differ by +/- 90 calendar days"
                                                " from the date when read in.")

        # TODO(Jacques Dafflon) Properly validate bank clearing no. of the client
