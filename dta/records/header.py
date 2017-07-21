from datetime import date, timedelta, datetime

from dta.constants import FillDirection
from dta.fields import Date, AlphaNumeric, Numeric
from dta.records.common import FieldsValidationMixin


class DTAHeader(FieldsValidationMixin):

    processing_date = Date(required=False)
    recipient_clearing = AlphaNumeric(length=12, required=False)
    creation_date = Date()
    client_clearing = AlphaNumeric(length=7, required=False)
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
            processing_date=self.processing_date.generate(),
            recipient_clearing=self.recipient_clearing.generate(),
            creation_date=self.creation_date.generate(),
            client_clearing=self.client_clearing.generate(),
            sender_id=self.sender_id.generate(),
            sequence_nr=self.sequence_nr.generate(),
            transaction_type=self.transaction_type.generate(),
            payment_type=self.payment_type.generate()
        )

    def validate(self):
        now = datetime.now()
        ninety_days_ago = now - timedelta(days=90)
        ninety_days_ahead = now + timedelta(days=90)
        if not isinstance(self.creation_date.value, date):
            format_errors = [f"[{self.__class__.__name__}] INVALID: creation date must contain a valid date."]
        elif not (ninety_days_ago < self.creation_date < ninety_days_ahead):
            format_errors = [(f"[{self.__class__.__name__}] INVALID: creation date may not differ by +/- 90 calendar "
                              f"days 'from the date when read in.")]
        else:
            format_errors = []

        # TODO Properly validate bank clearing no. of the client

        return [], [], format_errors

    def check(self):
        super(DTAHeader, self).check()
        if (self.transaction_code in ['830', '832', '836', '837', '890'] and
                self.processing_date != '000000'):
            raise DTAValueError('Processing date must be empty')
        if (self.transaction_code in ['826', '827'] and
                not self.processing_date.strip()):
            raise DTAValueError('Processing date must not be empty')
        if (self.transaction_code in ('826', '830', '832', '836', '837') and
                self.recipient_clearing_nr.strip()):
            raise DTAValueError('Recipient clearing number must be empty')
        if self.transaction_code not in ('826', '827', '830', '832', '836',
                '837', '890'):
            raise DTAValueError("Invalid transaction code '%s'" %
                    self.transaction_code)
        if self.payment_type not in ('0', '1'):
            raise DTAValueError("Invalid payment type '%s'" %
                    self.payment_type)
        if (self.transaction_code in ('826', '830', '832', '890') and
                self.payment_type != '0'):
            raise DTAValueError('Payment type must be 0')
