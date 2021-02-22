# wildlife-cam

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

### Update Wildlife Cam
1. Connect to your RPi using ssh `ssh pi@<IP of RPi>` and your password
2. Run update script `cd /home/pi/WildlifeCam/wildlife-cam/scripts; chmod +x wildlife-cam-update.sh; ./wildlife-cam-update.sh`




