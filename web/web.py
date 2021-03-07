#!/usr/bin/env python3

import configparser
import os
from flask import Flask, render_template, request
from config_form import ConfigForm

app = Flask(__name__)


def load_config():
    config = configparser.ConfigParser()
    config.read("/home/pi/WildlifeCam/WildlifeCam.ini")
    return config


@app.route('/', methods=['post'])
def config_form():
    form = ConfigForm()
    if form.validate_on_submit():
        config = load_config()

        gpio_pin = form.gpio_pin.data
        config.set('PirSensor', 'Pin', str(gpio_pin))

        telegram_enabled = form.telegram_enabled.data
        telegram_api_key = form.telegram_api_key.data
        telegram_chat_id = form.telegram_chat_id.data
        if telegram_enabled:
            if not config.has_section('Telegram'):
                config.add_section('Telegram')
            config.set('Telegram', 'ApiKey', telegram_api_key)
            config.set('Telegram', 'ChatId', telegram_chat_id)
        else:
            if config.has_section('Telegram'):
                config.remove_section('Telegram')

        with open('/home/pi/WildlifeCam/WildlifeCam.ini', 'w') as configfile:
            config.write(configfile)

        os.system("sudo systemctl restart wildlife-cam")

    return render_template('index.html', form=form)


@app.route('/', methods=['get'])
def index():
    config = load_config()

    form = ConfigForm()
    form.gpio_pin.data = config.getint('PirSensor', 'Pin')

    form.telegram_enabled.data = config.has_section('Telegram')
    form.telegram_api_key.data = config.get('Telegram', 'ApiKey')
    form.telegram_chat_id.data = config.get('Telegram', 'ChatId')

    return render_template('index.html', form=form)


if __name__ == '__main__':
    app.config['SECRET_KEY'] = 'any secret string'
    app.run(host='0.0.0.0', debug=True)
