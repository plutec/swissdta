from decimal import Decimal
from sys import stderr

from dta.constants import CONVERTED_CHARACTERS


class Field(object):
    def __init__(self, length: int, required: bool = True, value=None):
        print('Field init')
        self.length = length
        self.required = required
        self.__set__(self, value)

    def __set__(self, instance, value):
        print(f'field set: {instance} {value} ')
        self.value = value

    def __get__(self, instance, owner) -> str:
        print(f'{self} {instance} {owner}')
        print(f'get: {instance} {owner} -> {self.value}')
        return self.value

    # def __str__(self):
    #     return str(self.value)

    def validate(self) -> [str]:
        if self.value is not None and len(self.value) > self.length:
            return [f'[{self.__class__.__name__}] TOO LONG: {self.value} can be at most {self.length} characters']
        return []


class AlphaNumeric(Field):
    def __init__(self, *args, clipping=False, value: str = '', **kwargs):
        self.clipping = clipping
        super(AlphaNumeric, self).__init__(*args, value=value, **kwargs)

    def __get__(self, instance, owner) -> str:
        return ''.join(CONVERTED_CHARACTERS.get(ord(char), char) for char in self.value)

    def __set__(self, instance, value: str):
        if self.clipping and len(self.value) > self.length:  # if clipping is True, value is truncated automatically
            new_value = value[:self.length]                  # and will always be of valid length
            print((f'[{self.__class__.__name__}] WARNING: ' 
                   f'{value} over {self.length} characters long, truncating to {new_value}'), file=stderr)
            value = new_value
        super(AlphaNumeric, self).__set__(instance, value)


class Numeric(Field):

    def __get__(self, instance, owner) -> str:
        return f'{super().__get__(instance, owner)}'

    def __set__(self, instance, value: int):
        super().__set__(instance, value)


class Amount(Field):

    def __init__(self, length: int, required: bool = True, value: Decimal = None):
        super().__init__(length, required, value)

    def __get__(self, instance, owner) -> str:
        _, digits, exp = self.value.as_tuple()
        if exp == 0:
            return f'{self.value},'
        integers = ''.join(f'{d}' for d in digits[:exp])
        decimals = ''.join(f'{d}' for d in digits[exp:])
        return f'{integers},{decimals}'

    def __set__(self, instance, value: Decimal):
        super().__set__(instance, value)

    def validate(self):
        errors = super().validate()
        if self.value.is_zero():
            errors.append(f'[{self.__class__.__name__}] INVALID: May not be zero')
        elif self.value.is_signed():  # Amount must be positive
            errors.append(f'[{self.__class__.__name__}] INVALID: May not be negative')
        return errors

