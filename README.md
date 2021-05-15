# wildlife-cam
Wildlife-cam is a relatively inexpensive motion detection wildlife camera that I use to take unobserved wildlife in my garden - mostly squirrels!

## Materials and Tools
This project uses a raspberry pi zero, a raspberry pi camera module, a PIR sensor and a power bank.

### Materials
1. [Raspberry Pi Zero W](https://www.reichelt.de/raspberry-pi-zero-w-v-1-1-1-ghz-512-mb-ram-wlan-bt-rasp-pi-zero-w-p256438.html?&nbc=1)
2. [Raspberry Pi Camera V2](https://www.reichelt.de/raspberry-pi-kamera-8mp-v2-1-imx219pq-rasp-cam-2-p170853.html?&nbc=1)
   including the right [cable](https://www.reichelt.de/raspberry-pi-zero-flexkabel-fuer-standard-kameramodul-15cm-rpiz-cam-fl15-p223615.html?&nbc=1)
3. [PIR sensor](https://www.reichelt.de/raspberry-pi-infrarot-bewegungsmelder-pir-hc-sr501-rpi-hc-sr501-p224216.html?&nbc=1)
4. Any power bank, I got [this one](https://www.reichelt.de/powerbank-li-po-10000-mah-slim-2x-usb-schwarz-vt-8897-p264462.html?&nbc=1)
5. [Optional] on-off switch and an addition usb cable for your powerbank

### Tools
1. Solder gun and solder
2. Wire cutters
3. Hot glue gun and hot glue
4. 3D printer for [the case](https://www.thingiverse.com/thing:4859312)

## Installation

### Setup Raspberry PI
1. Flash latest RPi OS (tested with buster) to sc-card, e.g. using Raspberry PI Imager
2. Configure Wifi
    1. `touch ssh`
    2. `touch wpa_supplicant.conf` ([more info](https://www.raspberrypi.org/documentation/configuration/wireless/headless.md))
    3. Example Wifi config for `wpa_supplicant.conf`
    ```
    ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
    update_config=1
    country=<Insert 2 letter ISO 3166-1 country code here>

    network={
      ssid="<Name of your wireless LAN>"
      psk="<Password for your wireless LAN>"
    }
    ```
3. Connect to your RPi using ssh `ssh pi@<IP of RPi>` and password `raspberry`
4. Change password using `passwd`
5. Enable Camera using `sudo raspi-config` ([more info](https://www.raspberrypi.org/documentation/configuration/raspi-config.md))
6. Reboot RPi if asked

### Setup Wildlife Cam
1. Connect to your RPi using ssh `ssh pi@<IP of RPi>` and your password
2. Install Wildlife Cam using the one line install script `cd; rm wildlife-cam-install.sh 2>/dev/null; wget https://raw.githubusercontent.com/SteffiPeTaffy/wildlife-cam/main/scripts/wildlife-cam-install.sh; chmod +x wildlife-cam-install.sh; ./wildlife-cam-install.sh`
3. [Optional] Configure FTP Upload 
4. [Optional] Configure Telegram Chat Bot

### Update Wildlife Cam
1. Connect to your RPi using ssh `ssh pi@<IP of RPi>` and your password
2. Run update script `cd /home/pi/WildlifeCam/wildlife-cam/scripts; chmod +x wildlife-cam-update.sh; ./wildlife-cam-update.sh`

### Logs
See system service logs by running `sudo journalctl -u wildlife-cam -f` or `sudo journalctl -u wildlife-cam-web -f`


## Features

### Overview
* Motion detection
   * Snap Photo on motion detected
   * Snap Series of Photos on motion detected (defaults to 3 pictures)
   * Record Video Clip on motion detected (defaults 5 seconds)
* FTP Upload  
   * Upload media via FTP (if setup during installation or using web config)
* Telegram Integration  
   * Send Media to Telegram Chat using a Telegram Chatbot (if setup during installation or using web config)
   * Pause motion detection using preconfigured Telegram bot command (defaults to 60 seconds)
   * Stop/start motion detection using preconfigured Telegram bot command
   * Snap picture/series using preconfigured Telegram bot command
   * Record video clip using preconfigured Telegram bot command
* Configuration   
   * Configure Wildlife Cam using web app available on <IP of RPi>:5000


