from datetime import date
from decimal import Decimal
from enum import Enum
from weakref import WeakKeyDictionary

from iso4217 import Currency as CurrencyCode
from schwifty import IBAN

from dta.constants import CONVERTED_CHARACTERS


class Field(object):
    def __init__(self, length: int, required: bool = True, value=None):
        self.length = length
        self.required = required
        self.data = WeakKeyDictionary()
        self.default = value

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner) -> str:
        return self._format_value(self.data.get(instance, self.default))

    def __set__(self, instance, value):
        warnings, errors = self.validate(value)
        if warnings:
            instance.field_warnings[self.name] = warnings
        if errors:
            instance.field_errors[self.name] = errors

        self.data[instance] = value

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.name}>'

    def _format_value(self, value) -> str:
        return (value if value is not None else '').ljust(self.length, fillchar=' ')

    def validate(self, value) -> [str]:
        formatted_value = self._format_value(value)
        if len(formatted_value) > self.length:
            errors = [f'[{self.name}] TOO LONG: {formatted_value} can be at most {self.length} characters']
        else:
            errors = []
        return [], errors


class AllowedValuesMixin(object):
    def __init__(self, *args, **kwargs):
        self.allowed_values = kwargs.pop('allowed_values', set())
        if isinstance(self.allowed_values, Enum):
            self.allowed_values = set(item.value for item in self.allowed_values)
        super().__init__(*args, **kwargs)

    def validate(self, value):
        warnings, errors = super().validate(value)
        if value not in self.allowed_values:
            errors.append(f'[{self.name}] INVALID: Only {self.allowed_values} permitted (got: {value})')
        return warnings, errors


class AlphaNumeric(AllowedValuesMixin, Field):
    def __init__(self, *args, clipping=False, value: str = '', **kwargs):
        self.clipping = clipping
        super(AlphaNumeric, self).__init__(*args, value=value, **kwargs)

    def __set__(self, instance, value: str):
        if self.clipping and len(value) > self.length:  # if clipping is True, value is truncated automatically
            new_value = value[:self.length]                  # and will always be of valid length
            warning = f'[{self.name}] WARNING: {value} over {self.length} characters long, truncating to {new_value}'
            value = new_value
        else:
            warning = None
        super(AlphaNumeric, self).__set__(instance, value)
        if warning:
            if self.name in instance.field_warnings:
                instance.field_warnings[self.name].append(warning)
            else:
                instance.field_warnings[self.name] = [warning]

    def _format_value(self, value: str) -> str:
        return super()._format_value(''.join(CONVERTED_CHARACTERS.get(ord(char), char) for char in value))


class Numeric(AllowedValuesMixin, Field):
    def __init__(self, length: int, required: bool = True, value: int = None):
        super().__init__(length, required, value)

    def __set__(self, instance, value: int):
        super().__set__(instance, value)

    def _format_value(self, value: int) -> str:
        return super()._format_value(f'{value}')


class Amount(Field):
    def __init__(self, length: int, required: bool = True, value: Decimal = Decimal(0)):
        super().__init__(length, required, value)

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
        warnings, errors = super().validate(value)
        if value.is_zero():
            errors.append(f'[{self.__class__.__name__}] INVALID: May not be zero')
        elif value.is_signed():  # Amount must be positive
            errors.append(f'[{self.__class__.__name__}] INVALID: May not be negative')
        return warnings, errors


class Currency(Field):
    def __init__(self, length=3, required: bool =True, value=None):  # ISO code for currencies is exactly 3 letters
        super().__init__(length, required, value)

    def __set__(self, instance, value: str):
        super().__set__(instance, value.upper() if value is not None else value)

    def validate(self, value: str):
        warnings, errors = super(Currency, self).validate(value)
        try:
            CurrencyCode(value)
        except ValueError as err:
            errors.append(str(err))
        finally:
            return warnings, errors


class Iban(Field):
    def __init__(self, length: int, required: bool = True, value: str = ''):
        super().__init__(max(length, 34), required, value)

    def __set__(self, instance, value: str):
        super().__set__(instance, IBAN(value, allow_invalid=True))

    def validate(self, value: IBAN):
        warnings, errors = super().validate(value)
        try:
            value.validate()
        except ValueError as err:
            errors.append(str(err))
        finally:
            return warnings, errors

    def _format_value(self, value: IBAN) -> str:
        return super()._format_value(value.compact)


class Date(Field):
    DEFAULT_DATE = '000000'

    def __init__(self, length=6, required: bool = True, value: date = None):
        super().__init__(length, required, value)

    def __set__(self, instance, value: date):
        super().__set__(instance, value)

    def validate(self, value):
        warnings, errors = super().validate(value)
        if value is not None and not isinstance(value, date):
            errors.append(f"[{self.name}] INVALID: date must contain a valid date or None ({self.DEFAULT_DATE}).")
        return warnings, errors

    def _format_value(self, value: date) -> str:
        if value is None:
            formatted_date = self.DEFAULT_DATE
        elif isinstance(value, date):
            formatted_date = value.strftime('%y%m%d')  # Date field must conform to the format YYMMDD (year, month, day)
        else:
            formatted_date = value

        return super()._format_value(formatted_date)
