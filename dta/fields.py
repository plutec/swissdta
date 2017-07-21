from datetime import date
from decimal import Decimal
from enum import Enum, EnumMeta
from weakref import WeakKeyDictionary

from iso4217 import Currency as CurrencyCode
from schwifty import IBAN

from dta.constants import CONVERTED_CHARACTERS, FillDirection


class Field(object):
    def __init__(self, length: int, value=None, fillchar: str = ' ', filldir: FillDirection = FillDirection.RIGHT):
        self.length = length
        self.data = WeakKeyDictionary()
        self.default = value
        self.fillchar = fillchar
        self.filldir = filldir

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner) -> str:
        return self._format_value(self.data.get(instance, self.default))

    def __set__(self, instance, value):
        instance.set_warnings(self.name)  # remove all warnings on new value
        instance.set_errors(self.name, *self.validate(value))
        self.data[instance] = value

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.name}>'

    def _format_value(self, value) -> str:
        if self.filldir == FillDirection.LEFT:
            return (value if value is not None else '').rjust(self.length, self.fillchar)
        elif self.filldir == FillDirection.RIGHT:
            return (value if value is not None else '').ljust(self.length, self.fillchar)

    def validate(self, value) -> [str]:
        formatted_value = self._format_value(value)
        if len(formatted_value) > self.length:
            return [f"TOO LONG: {formatted_value} can be at most {self.length} characters"]
        return []


class AllowedValuesMixin(object):
    def __init__(self, *args, **kwargs):
        self.allowed_values = kwargs.pop('allowed_values', set())
        if isinstance(self.allowed_values, EnumMeta):
            self.allowed_values = set(item.value for item in self.allowed_values)

        if isinstance(kwargs.get('value'), Enum):
            kwargs['value'] = kwargs['value'].value

        super().__init__(*args, **kwargs)

    def __set__(self, instance, value):
        if isinstance(value, Enum):
            value = value.value
        super().__set__(instance, value)

    def validate(self, value):
        if not self.allowed_values:
            return []
        errors = super().validate(value)
        if value not in self.allowed_values:
            errors.append(f'INVALID: Only {self.allowed_values} permitted (got: {value})')
        return errors


class AlphaNumeric(AllowedValuesMixin, Field):
    def __init__(self, length: int, *args, clipping=False, value: str = '', **kwargs):
        self.clipping = clipping
        super().__init__(length, *args, value=value, **kwargs)

    def __set__(self, instance, value: str):
        if self.clipping and len(value) > self.length:  # if clipping is True, value is truncated automatically
            new_value = value[:self.length]             # and will always be of valid length
            value = new_value
            clipped = True
        else:
            clipped = False

        super(AlphaNumeric, self).__set__(instance, value)

        if clipped:  # must add the warning after call to super which set the initial warnings and errors
            instance.add_warning(self.name,
                                 f'WARNING: {value} over {self.length} characters long, truncating to {new_value}')

    def _format_value(self, value: str) -> str:
        return super()._format_value(''.join(CONVERTED_CHARACTERS.get(ord(char), char) for char in value))


class Numeric(AllowedValuesMixin, Field):
    def __init__(self, length: int, *args, value: int = None, **kwargs):
        super().__init__(length, *args, value=value, **kwargs)

    def __set__(self, instance, value: int):
        super().__set__(instance, value)

    def _format_value(self, value: int) -> str:
        return super()._format_value(f'{value}')


class Amount(Field):
    def __init__(self, length: int, *args, value: Decimal = Decimal(0), **kwargs):
        super().__init__(length, *args, value=value, **kwargs)

    def __set__(self, instance, value: Decimal):
        super().__set__(instance, value)

    def _format_value(self, value: Decimal) -> str:
        _, digits, exp = value.as_tuple()

        if exp == 0:
            formatted_amount = f'{value},'
        else:
            integers = ''.join(f'{d}' for d in digits[:exp])
            decimals = ''.join(f'{d}' for d in digits[exp:])
            formatted_amount = f'{integers},{decimals}'
        return super()._format_value(formatted_amount)

    def validate(self, value: Decimal):
        errors = super().validate(value)
        if value.is_zero():
            errors.append('INVALID: May not be zero')
        elif value.is_signed():  # Amount must be positive
            errors.append('INVALID: May not be negative')
        return errors


class Currency(Field):
    def __init__(self, length=3, *args, value=None, **kwargs):  # ISO code for currencies is exactly 3 letters
        super().__init__(length, *args, value=value, **kwargs)

    def __set__(self, instance, value: str):
        super().__set__(instance, value.upper() if value is not None else value)

    def validate(self, value: str):
        errors = super(Currency, self).validate(value)
        try:
            CurrencyCode(value)
        except ValueError as err:
            errors.append(str(err))
        finally:
            return errors


class Iban(Field):
    def __init__(self, length: int, *args, value: str = '', **kwargs):
        super().__init__(max(length, 34), *args, value=value, **kwargs)

    def __set__(self, instance, value: str):
        super().__set__(instance, IBAN(value, allow_invalid=True))

    def validate(self, value: IBAN):
        errors = super().validate(value)
        try:
            value.validate()
        except ValueError as err:
            errors.append(str(err))
        finally:
            return errors

    def _format_value(self, value: IBAN) -> str:
        return super()._format_value(value.compact)


class Date(Field):
    DATE_FORMAT = '%y%m%d'
    DEFAULT_DATE = '000000'

    def __init__(self, length=6, *args, value: date = None, **kwargs):
        super().__init__(length, *args, value=value, **kwargs)

    def __set__(self, instance, value: date):
        super().__set__(instance, value)

    def validate(self, value):
        errors = super().validate(value)
        if value is not None and not isinstance(value, date):
            errors.append(f"[{self.name}] INVALID: date must contain a valid date or None ({self.DEFAULT_DATE}).")
        return errors

    def _format_value(self, value: date) -> str:
        if value is None:
            formatted_date = self.DEFAULT_DATE
        elif isinstance(value, date):
            formatted_date = value.strftime('%y%m%d')  # Date field must conform to the format YYMMDD (year, month, day)
        else:
            formatted_date = value

        return super()._format_value(formatted_date)
