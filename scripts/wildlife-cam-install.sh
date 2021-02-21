#!/bin/bash
#
# see https://github.com/SteffiPeTaffy/wildlife-cam for details

readonly HOME_DIR=/home/pi/
readonly BASE_DIR_NAME=WildlifeCam/
readonly PHOTO_DIR_NAME=Photos/
readonly GIT_BASE_DIR_NAME=wildlife-cam
readonly CONFIG_FILE_NAME=WildlifeCam.ini

clear
echo "#####################################################
#            _ _    _ _ _  __                       #
#    __ __ _(_) |__| | (_)/ _|___   __ __ _ _ __    #
#    \ V  V / | / _` | | |  _/ -_) / _/ _` | '  \   #
#     \_/\_/|_|_\__,_|_|_|_| \___| \__\__,_|_|_|_|  #
#                                                   #
#####################################################

Welcome to the installation script.

This script will install Wildlife Cam on your Raspberry Pi.
If you are ready, hit ENTER"

read -r INPUT

# Make sure everything is up-to-date
sudo apt-get update

# Remove python 2.7 that comes with Raspbian
sudo apt-get remove python
sudo apt autoremove

# Install python 3
sudo apt-get --yes install python3
sudo apt-get --yes install python3-rpi.gpio
sudo apt-get --yes install python3-smbus

# Install dependencies
sudo apt-get --yes install git
sudo apt install --yes python3-gpiozero
sudo apt-get install --yes python3-picamera
sudo apt-get install --yes python3-requests

# Check if Wildlife Cam folder already exists
cd ${HOME_DIR} || exit
if [ -d "${HOME_DIR}${BASE_DIR_NAME}" ]; then

  echo "It looks like you have already installed Wildlife Cam"
  echo "Installing it again will delete all photos and configurations"
  echo -n "Continue anyways? [y/n]"
  read answer
  if [ "$answer" != "${answer#[Nn]}" ] ;then
      exit 1
  else
      sudo rm -r ${BASE_DIR_NAME}
  fi
fi

# Create folder for all Wildlife Cam related artefacts
mkdir ${BASE_DIR_NAME}
cd ${BASE_DIR_NAME}

# create config file
touch ${CONFIG_FILE_NAME}

# create folder for photos
mkdir ${PHOTO_DIR_NAME}
echo -e "[General]" >> ${CONFIG_FILE_NAME}
echo -e "PhotoDirPath=\"${HOME_DIR}${BASE_DIR_NAME}${PHOTO_DIR_NAME}\"" >> ${CONFIG_FILE_NAME}
echo -e "" >> ${CONFIG_FILE_NAME}

# Configure Telegram
echo -n "Want to setup Telegram? [y/n]"
read answer
if [ "$answer" != "${answer#[Yy]}" ] ;then
    read -rp "Type Telegram API Token (like 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11): " TELEGRAM_API_TOKEN
    read -rp "Type Telegram Chat ID (like 0123456789): " TELEGRAM_CHAT_ID
    echo ""
    echo "Your Telegram details:"
    echo "Api Token : $TELEGRAM_API_TOKEN"
    echo "Chat Id   : $TELEGRAM_CHAT_ID"
    echo -e "[Telegram]" >> ${CONFIG_FILE_NAME}
    echo -e "ApiKey=\"$TELEGRAM_API_TOKEN\"" >> ${CONFIG_FILE_NAME}
    echo -e "ChatId=\"$TELEGRAM_CHAT_ID\"" >> ${CONFIG_FILE_NAME}
    echo -e "" >> ${CONFIG_FILE_NAME}
fi

# Get github code
git clone https://github.com/SteffiPeTaffy/wildlife-cam.git ${GIT_BASE_DIR_NAME}

echo
echo "DONE. Let's watch some squirrels :)"
echo "Find more information on the github account:"
echo "https://github.com/SteffiPeTaffy/wildlife-cam"
echo ""

# run wildlife cam
cd "${HOME_DIR}${BASE_DIR_NAME}${GIT_BASE_DIR_NAME}" || exit
python3 wildlife-cam.py "${HOME_DIR}${BASE_DIR_NAME}${CONFIG_FILE_NAME}"

