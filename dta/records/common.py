from collections import defaultdict


class ValidationHandler(object):

    def __init__(self, *args, **kwargs):
        self.field_warnings = defaultdict(list)
        self.field_errors = defaultdict(list)

    def add_warning(self, field_name: str, warning: str):
        self.field_warnings[field_name].append(f'[{field_name}] {warning}')

    def set_warnings(self, field_name: str, *warnings: str):
        self.field_warnings[field_name] = [f'[{field_name}] {warning}' for warning in warnings]

    def add_error(self, field_name: str, error: str):
        self.field_errors[field_name].append(f'[{field_name}] {error}')

    def set_errors(self, field_name: str, *errors: str):
        self.field_errors[field_name] = [f'[{field_name}] {error}' for error in errors]

    def has_errors(self):
        return any(self.field_errors.values())
