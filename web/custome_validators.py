from wtforms.validators import Optional, InputRequired


class RequiredIf(InputRequired):
    field_flags = ('requiredif',)

    def __init__(self, other_field_name, message=None, *args, **kwargs):
        self.other_field_name = other_field_name
        self.message = message

    def __call__(self, form, field):
        other_field = form[self.other_field_name]
        if other_field is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)
        if other_field.data == 'No':
            Optional().__call__(form, field)
        else:
            super(RequiredIf, self).__call__(form, field)
