#!/bin/bash
#
# see https://github.com/SteffiPeTaffy/wildlife-cam for details

# The absolute path to the folder which contains this script


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

# Install required packages
sudo apt-get update
