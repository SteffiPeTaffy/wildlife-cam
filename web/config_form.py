from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, BooleanField
from wtforms.validators import DataRequired

from custome_validators import RequiredIf


class ConfigForm(FlaskForm):
    gpio_pin = IntegerField("GPIO Pin: ", validators=[DataRequired()])
    telegram_enabled = BooleanField("Telegram")
    telegram_api_key = PasswordField("API Key")
    telegram_chat_id = StringField("Chat ID", validators=[RequiredIf('telegram_enabled')])
    ftp_enabled = BooleanField("FTP Upload")
    ftp_ip_address = StringField("IP Address", validators=[RequiredIf('ftp_enabled')])
    ftp_ip_port = IntegerField("Port", validators=[RequiredIf('ftp_enabled')])
    ftp_ip_user = StringField("User", validators=[RequiredIf('ftp_enabled')])
    ftp_ip_password = PasswordField("Password")
    ftp_ip_directory = StringField("Directory", validators=[RequiredIf('ftp_enabled')])
    submit = SubmitField("Submit")
