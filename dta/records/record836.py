from dta.constants import IdentificationBankAddress, IdentificationPurpose, ChargesRule
from dta.fields import AlphaNumeric, Date, Currency, Amount, Numeric, Iban
from .record import DTARecord


class DTARecord836(DTARecord):

    reference = AlphaNumeric(length=11)
    client_account = AlphaNumeric(length=24)
    value_date = Date()
    currency = Currency()
    amount = Amount(length=15)

    conversation_rate = Amount(length=12, required=False)
    client_address1 = AlphaNumeric(length=35, clipping=True)
    client_address2 = AlphaNumeric(length=35, clipping=True)
    client_address3 = AlphaNumeric(length=35, clipping=True)

    bank_address_type = AlphaNumeric(length=1, allowed_values=IdentificationBankAddress)
    bank_address1 = AlphaNumeric(length=35, required=False)
    bank_address2 = AlphaNumeric(length=35, required=False)
    recipient_iban = Iban(length=34)

    recipient_name = AlphaNumeric(length=35, clipping=True)
    recipient_address1 = AlphaNumeric(length=35, clipping=True)
    recipient_address2 = AlphaNumeric(length=35, clipping=True)

    identification_purpose = AlphaNumeric(length=1, allowed_values=IdentificationPurpose)
    purpose1 = AlphaNumeric(length=35, required=False)
    purpose2 = AlphaNumeric(length=35, required=False)
    purpose3 = AlphaNumeric(length=35, required=False)
    charges_rules = Numeric(length=1, allowed_values=ChargesRule)

    _template = (
        '01{header}{reference}{client_account}{value_date}{currency}{amount}{padding:<11}\r\n'
        '02{conversation_rate}{client_address1}{client_address2}{client_address3}{padding:<9}\r\n'
        '03{bank_address_type}{bank_address1}{bank_address2}{recipient_iban}{padding:<21}\r\n'
        '04{recipient_name}{recipient_address1}{recipient_address2}{padding:<21}\r\n'
        '05{identification_purpose}{purpose1}{purpose2}{purpose3}{charges_rules}{padding:<19}\r\n'
    )

    def __init__(self, processing_date, creation_date, client_clearing, sender_id, sequence_nr):
        super().__init__(processing_date=processing_date,
                         recipient_clearing='',
                         creation_date=creation_date,
                         client_clearing=client_clearing,
                         sender_id=sender_id,
                         sequence_nr=sequence_nr)
        self.header.transaction_code = 836

    def generate(self):
        return self._template.format(
            header=self.header.generate(),
            # First 5 positions must contain a valid DTA identification (sender id).
            # Remaining 11 positions must contain a transaction reference number.
            # The generation of the full (16x) reference from the valid DTA identification is done automatically here
            reference=f'{self.header.sender_id.generate()}{self.reference.generate()}',
            client_account=self.client_account.generate(),
            value_date=self.value_date.generate(),
            currency=self.currency.generate(),
            amount=self.amount.generate(),

            conversation_rate=self.conversation_rate.generate(),
            client_address1=self.client_address1.generate(),
            client_address2=self.client_address2.generate(),
            client_address3=self.client_address3.generate(),

            bank_address_type=self.bank_address_type.generate(),
            bank_address1=self.bank_address1.generate(),
            bank_address2=self.bank_address2.generate(),
            recipient_iban=self.recipient_iban.generate(),

            recipient_name=self.recipient_name.generate(),
            recipient_address1=self.recipient_address1.generate(),
            recipient_address2=self.recipient_address2.generate(),

            identification_purpose=self.identification_purpose.generate(),
            purpose1=self.purpose1.generate(),
            purpose2=self.purpose2.generate(),
            purpose3=self.purpose3.generate(),
            charges_rules=self.charges_rules.generate(),

            padding=''
        )
