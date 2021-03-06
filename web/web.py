#!/usr/bin/env python3

import configparser
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
        gpio_pin = form.gpio_pin.data
        print(gpio_pin)

        config = load_config()
        config.set('PirSensor', 'Pin', str(gpio_pin))
        with open('/home/pi/WildlifeCam/WildlifeCam.ini', 'w') as configfile:
            config.write(configfile)

    return render_template('index.html', form=form)


@app.route('/', methods=['get'])
def index():
    config = load_config()

    form = ConfigForm()
    form.gpio_pin.data = config.getint('PirSensor', 'Pin')

    return render_template('index.html', form=form)


if __name__ == '__main__':
    app.config['SECRET_KEY'] = 'any secret string'
    app.run(host='0.0.0.0', debug=True)
