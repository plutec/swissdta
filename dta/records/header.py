from datetime import date, timedelta, datetime

from dta.constants import FillDirection
from dta.fields import Date, AlphaNumeric, Numeric
from dta.records.common import FieldsValidationMixin


class DTAHeader(FieldsValidationMixin):

    processing_date = Date()
    recipient_clearing = AlphaNumeric(length=12)
    creation_date = Date()
    client_clearing = AlphaNumeric(length=7)
    sender_id = AlphaNumeric(length=5)
    sequence_nr = Numeric(length=5, fillchar='0', filldir=FillDirection.LEFT)
    transaction_type = Numeric(length=3)
    payment_type = Numeric(length=1, value=0)
    processing_flag = Numeric(length=1, value=0)

    _template = ('{processing_date}{recipient_clearing}00000'
                 '{creation_date}{client_clearing}{sender_id}{sequence_nr}{transaction_type}{payment_type}0')

    def __init__(self, processing_date, recipient_clearing, creation_date, client_clearing, sender_id, sequence_nr
                 ) -> None:
        super().__init__()
        self.processing_date = processing_date
        self.recipient_clearing = recipient_clearing
        self.creation_date = creation_date
        self.client_clearing = client_clearing
        self.sender_id = sender_id
        self.sequence_nr = sequence_nr

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

        # TODO Properly validate bank clearing no. of the client
