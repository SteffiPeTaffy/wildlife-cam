from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField
from wtforms.validators import DataRequired


class ConfigForm(FlaskForm):
    gpio_pin = IntegerField("PIR Sensor Pin: ", validators=[DataRequired()])
    submit = SubmitField("Submit")
