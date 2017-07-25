# DTA [![Build Status](https://travis-ci.org/jacquesd/dta.svg?branch=master)](https://travis-ci.org/jacquesd/dta) [![codecov](https://codecov.io/gh/jacquesd/dta/branch/master/graph/badge.svg)](https://codecov.io/gh/jacquesd/dta)


Generator library for Swiss DTA ("Datenträgeraustauschverfahren") electronic payment records loosely inspired by
[python-dta](https://pypi.python.org/pypi/python-dta).

## Author
Jacques Dafflon <[jacques.dafflon@gmail.com](mailto:jacques.dafflon@gmail.com)>

## Disclaimer
Please review and test te library with your infrastructure before using it.

The author does not guarantee that this library will generate valid DTA records and is in no way responsible
for any financial issues (including but not limited to: failure of payments, payments to wrong party,
incorrect payment amount, financial lost).

By using this library you agree to this disclaimer.

## License
Distributed under the [MIT License](https://github.com/jacquesd/dta/blob/master/LICENSE)

## Features

- Support for transaction types 836, 890
- Implements most of the validations rules sepcified in the
[DTA Standards and Formats](https://www.six-interbank-clearing.com/dam/downloads/en/standardization/dta/dta.pdf).
- Supports `Decimal`, `date` and IBAN with or without blanks as input values
- Automatic generation of TA 890 record
- Automatically handle sequence numbers
- Automatically use the sender identification for the first 5 characters of the reference (TA 836)
- Currency code check (via [iso4217](https://pypi.python.org/pypi/iso4217))
- Clipping of overlong Alphanumeric fields (such as addresses or purpose)
- Automatic conversion of permitted ISO Latincode 8859-1 characters
- Enum for fields with a constrained of valid values
(e.g. [`dta.constants.IdentificationPurpose`](https://github.com/jacquesd/dta/blob/master/dta/constants.py#L20-L22))
- Sane default values
- Generates a sequence of properly (latin-1) encoded bytes
- Type annotations

## Getting started

Generate a DTA file containing a single transaction of type 836:

```python
from datetime import date
from decimal import Decimal
from dta.constants import IdentificationPurpose, ChargesRule
from dta.dta import DTAFile
dta_file = DTAFile(sender_id='ABC12', client_clearing='8888')
dta_file.add_836_record(reference='01234567890',  # only 11 chars, the first 5 (sender id) are added automatically
                        client_account='CH38 0888 8123 4567 8901 2',
                        processing_date=date(2017, 7, 24),
                        currency='CHF',
                        amount=Decimal(10),
                        client_address=('Alphabet Inc', 'Brandschenkestrasse 110', '8002 Zürich'),
                        recipient_iban='CH9300762011623852957',
                        recipient_name='Herr Peter Haller',
                        recipient_address=('Marktplaz 4', '9400 Rorschach'),
                        identification_purpose=IdentificationPurpose.UNSTRUCTURED,
                        purpose=('DTA lib example', '', ''),
                        charges_rules=ChargesRule.OUR
                        )
print(dta_file.generate().decode('latin-1'))

"""
>>> print(dta_file.generate().decode('latin-1'))
01000000            000001707228888   ABC120000183600ABC1201234567890CH3808888123456789012   170724CHF10,                       
02            Alphabet Inc                       Brandschenkestrasse 110            8002 Zuerich                                
03D                                                                      CH9300762011623852957                                  
04Herr Peter Haller                  Marktplaz 4                        9400 Rorschach                                          
05UDTA lib  example                                                                                         1                   
01000000            00000170722       ABC12000028900010,                                                                        


"""
```

## Limitations
- The account to be debited (`client_account`) for TA 836 only accepts IBAN
- The benificiary's bank clearing number is not validated against a registry of banks to check if it is valid (TA 836).
- No IPI reference validation if the identification purpose is set to structured (TA 836).
- No parsing functionality of existing DTA files or records
- Lack of tests (should be fixed soon...)
