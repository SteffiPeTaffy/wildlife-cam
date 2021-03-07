from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, BooleanField
from wtforms.validators import DataRequired

from custome_validators import RequiredIf


class ConfigForm(FlaskForm):
    gpio_pin = IntegerField("PIR Sensor Pin: ", validators=[DataRequired()])
    telegram_enabled = BooleanField("Telegram")
    telegram_api_key = PasswordField("Telegram API Key: ", validators=[RequiredIf('telegram_enabled')])
    telegram_chat_id = StringField("Telegram Chat ID: ", validators=[RequiredIf('telegram_enabled')])
    ftp_enabled = BooleanField("FTP Upload")
    ftp_ip_address = StringField("FTP IP Address: ", validators=[RequiredIf('ftp_enabled')])
    ftp_ip_port = IntegerField("FTP Port: ", validators=[RequiredIf('ftp_enabled')])
    ftp_ip_user = StringField("FTP User: ", validators=[RequiredIf('ftp_enabled')])
    ftp_ip_password = PasswordField("FTP Password: ", validators=[RequiredIf('ftp_enabled')])
    ftp_ip_directory = StringField("FTP Directory: ", validators=[RequiredIf('ftp_enabled')])
    submit = SubmitField("Submit")
