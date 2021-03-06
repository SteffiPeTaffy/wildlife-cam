from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired


class ConfigForm(FlaskForm):
    gpio_pin = StringField("PIR Sensor Pin: ", validators=[DataRequired()])
    submit = SubmitField("Submit")
