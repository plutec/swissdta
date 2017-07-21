class FieldsValidationMixin(object):

    def __init__(self, *args, **kwargs):
        self.field_warnings = {}
        self.field_errors = {}
