from datetime import datetime, timedelta
from itertools import combinations

from schwifty import BIC, IBAN

from dta.constants import IdentificationBankAddress, IdentificationPurpose, ChargesRule
from dta.fields import AlphaNumeric, Date, Currency, Amount, Numeric, Iban
from dta.util import remove_whitespace
from .record import DTARecord


class DTARecord836(DTARecord):

    reference = AlphaNumeric(length=11)
    client_account = AlphaNumeric(length=24)
    value_date = Date()
    currency = Currency()
    amount = Amount(length=15)

    conversation_rate = Amount(length=12)
    client_address1 = AlphaNumeric(length=35, clipping=True)
    client_address2 = AlphaNumeric(length=35, clipping=True)
    client_address3 = AlphaNumeric(length=35, clipping=True)

    bank_address_type = AlphaNumeric(length=1, allowed_values=IdentificationBankAddress)
    bank_address1 = AlphaNumeric(length=35)
    bank_address2 = AlphaNumeric(length=35)
    recipient_iban = Iban(length=34)

    recipient_name = AlphaNumeric(length=35, clipping=True)
    recipient_address1 = AlphaNumeric(length=35, clipping=True)
    recipient_address2 = AlphaNumeric(length=35, clipping=True)

    identification_purpose = AlphaNumeric(length=1, allowed_values=IdentificationPurpose)
    purpose1 = AlphaNumeric(length=35)
    purpose2 = AlphaNumeric(length=35)
    purpose3 = AlphaNumeric(length=35)
    charges_rules = Numeric(length=1, allowed_values=ChargesRule)

    _template = (
        '01{header}{reference}{client_account}{value_date}{currency}{amount}{padding:<11}\r\n'
        '02{conversation_rate}{client_address1}{client_address2}{client_address3}{padding:<9}\r\n'
        '03{bank_address_type}{bank_address1}{bank_address2}{recipient_iban}{padding:<21}\r\n'
        '04{recipient_name}{recipient_address1}{recipient_address2}{padding:<21}\r\n'
        '05{identification_purpose}{purpose1}{purpose2}{purpose3}{charges_rules}{padding:<19}'
    )

    def __init__(self, ) -> None:
        super().__init__()
        self.header.transaction_type = 836

    @property
    def client_address(self):
        return self.client_address1, self.client_address2, self.client_address2

    @client_address.setter
    def client_address(self, client_address):
        self.client_address1, self.client_address2, self.client_address3 = client_address

    @property
    def bank_address(self):
        return self.bank_address1, self.bank_address2

    @bank_address.setter
    def bank_address(self, bank_address):
        self.bank_address1, self.bank_address2 = bank_address

    @property
    def recipient_address(self):
        return self.recipient_address1, self.recipient_address2

    @recipient_address.setter
    def recipient_address(self, recipient_address):
        self.recipient_address1, self.recipient_address2 = recipient_address

    @property
    def purpose(self):
        return self.purpose1, self.purpose2, self.purpose2

    @purpose.setter
    def purpose(self, purpose):
        self.purpose1, self.purpose2, self.purpose2 = purpose

    def generate(self):
        return self._template.format(
            header=self.header.generate(),
            # First 5 positions must contain a valid DTA identification (sender id).
            # Remaining 11 positions must contain a transaction reference number.
            # The generation of the full (16x) reference from the valid DTA identification is done automatically here
            reference=f'{self.header.sender_id}{self.reference}',
            client_account=self.client_account,
            value_date=self.value_date,
            currency=self.currency,
            amount=self.amount,

            conversation_rate=self.conversation_rate,
            client_address1=self.client_address1,
            client_address2=self.client_address2,
            client_address3=self.client_address3,

            bank_address_type=self.bank_address_type,
            bank_address1=self.bank_address1,
            bank_address2=self.bank_address2,
            recipient_iban=self.recipient_iban,

            recipient_name=self.recipient_name,
            recipient_address1=self.recipient_address1,
            recipient_address2=self.recipient_address2,

            identification_purpose=self.identification_purpose,
            purpose1=self.purpose1,
            purpose2=self.purpose2,
            purpose3=self.purpose3,
            charges_rules=self.charges_rules,

            padding=''
        )

    def validate(self):
        super().validate()
        if self.header.processing_date != '000000':
            self.header.add_error('processing_date', "NOT PERMITTED: header processing date must be '000000'.")

        if self.header.recipient_clearing.strip():
            self.header.add_error('recipient_clearing',
                                  "NOT ALLOWED: beneficiary's bank clearing number must be blank.")

        if self.header.transaction_type != '836':
            self.header.add_error('transaction_type', "INVALID: Transaction type must be TA 836.")

        if self.header.payment_type not in ('0', '1'):
            self.header.add_error('payment_type', "INVALID: Payment type must be 0 or 1 TA 836.")

        if not remove_whitespace(self.reference):
            self.add_error('reference', "MISSING TRANSACTION NUMBER: Reference may not be blank.")

        if len(self.client_account) > 16:  # Without IBAN, is 16 digits account no, otherwise assumed to be iban
            try:
                client_iban = IBAN(self.client_account, allow_invalid=False)
            except ValueError:  # Will throw ValueError if it is not a valid IBAN
                self.add_error(
                    'client_account',
                    "IBAN INVALID: Client account must be a valid with a 21 digit Swiss IBAN (CH resp. LI) ."
                )
            else:
                if client_iban.country_code not in ('CH', 'LI'):
                    self.add_error(
                        'client_account',
                        "IBAN INVALID: Client account must be a valid with a 21 digit Swiss IBAN (CH resp. LI) ."
                    )

        # Bank clearing is at pos 5-9 in IBAN
        if self.client_account[4:9].lstrip('0') != self.header.client_clearing.strip():
            self.add_error('client_account',
                           "IID IN IBAN NOT IDENTICAL WITH BC-NO: IID in IBAN (pos. 5 to 9) must concur with the "
                           "ordering party's BC no.")

        now = datetime.now()
        ten_days_ago = now - timedelta(days=10)
        sixty_days_ahead = now + timedelta(days=60)
        try:
            value_date = datetime.strptime(self.value_date, Date.DATE_FORMAT)
        except ValueError:
            self.add_error('value_date', "INVALID: Must contain a valid date.")
        else:
            if value_date < ten_days_ago:
                self.add_error('value_date', "EXPIRED: value date may not be elapsed more than 10 calendar days.")
            elif value_date > sixty_days_ahead:
                self.add_error('value_date', "TOO FAR AHEAD: value date may not exceed the reading in date + 60 days.")

        decimal_places = len(self.amount.strip().split(',', maxsplit=1)[1])
        if self.currency == 'CHF' and decimal_places > 2:
            self.add_error('currency',
                           "MORE THAN 2 DECIMAL PLACES: Amount may not contain more than 2 decimal places.")
        elif self.currency != 'CHF' and decimal_places > 3:
            self.add_error(
                'currency',
                " MORE THAN 3 DECIMAL PLACES: Amount may not contain more than 3 decimal places (foreign currencies)."
            )

        if self.amount.strip() == '0,':
            self.add_error('amount', "INVALID: Amount may not be zero.")

        if not any(self.client_address):
            self.add_error('client_address', "INCOMPLETE: Ordering party address, at least one line must exist.")
        if self.bank_address_type == IdentificationBankAddress.SWIFT_ADDRESS:
            try:
                BIC(self.bank_address1).validate()
            except ValueError:
                self.add_error(
                    'bank_address_type',
                    f"INCORRECT FIELD IDENTIFICATION: bank address type {IdentificationBankAddress.SWIFT_ADDRESS} "
                    f"may only be used if an 8 or 11 character BIC address (SWIFT) exists."
                )
        # No specification on how to validate a bank's address if the `bank_address_type` is not SWIFT.

        if all(not line1 or not line2 for line1, line2 in combinations(self.client_address, 2)):
            self.add_error('client_address', "INCOMPLETE: At least two address lines must exist.")

        if any('/C/' in address for address in self.client_address):
            self.add_error('client_address', "INVALID: /C/ may not be present for TA 836.")

        # TODO Validate IPI reference if identification purpose is structured (I)
