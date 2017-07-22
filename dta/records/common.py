from collections import defaultdict


class ValidationHandler(object):

    def __init__(self, *args, **kwargs):
        self.__validation_warnings = defaultdict(list)
        self.__validation_errors = defaultdict(list)

    @property
    def validation_warnings(self):
        return tuple(warning for warnings in self.__validation_warnings.values() for warning in warnings)

    @property
    def validation_errors(self):
        return tuple(error for errors in self.__validation_errors.values() for error in errors)

    def add_warning(self, field_name: str, warning: str):
        self.__validation_warnings[field_name].append(f'[{field_name}] {warning}')

    def set_warnings(self, field_name: str, *warnings: str):
        self.__validation_warnings[field_name] = [f'[{field_name}] {warning}' for warning in warnings]

    def add_error(self, field_name: str, error: str):
        self.__validation_errors[field_name].append(f'[{field_name}] {error}')

    def set_errors(self, field_name: str, *errors: str):
        self.__validation_errors[field_name] = [f'[{field_name}] {error}' for error in errors]

    def has_warnings(self):
        return any(self.__validation_warnings.values())

    def has_errors(self):
        return any(self.__validation_errors.values())
