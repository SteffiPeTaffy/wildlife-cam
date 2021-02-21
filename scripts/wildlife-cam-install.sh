#!/bin/bash
#
# see https://github.com/SteffiPeTaffy/wildlife-cam for details

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

# Get github code
cd /home/pi/ || exit
sudo rm -r wildlife-cam 2> /dev/null
git clone https://github.com/SteffiPeTaffy/wildlife-cam.git

echo
echo "DONE. Let's watch some squirrels :)"
echo "Find more information on the github account:"
echo "https://github.com/SteffiPeTaffy/wildlife-cam"
echo ""

# run wildlife cam
cd /home/pi/wildlife-cam || exit
python3 wildlife-cam.py

