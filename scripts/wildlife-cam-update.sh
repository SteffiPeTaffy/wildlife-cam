#!/bin/bash
#
# see https://github.com/SteffiPeTaffy/wildlife-cam for details

readonly HOME_DIR=/home/pi/
readonly BASE_DIR_NAME=WildlifeCam/
readonly GIT_BASE_DIR_NAME=wildlife-cam

# Make sure everything is up-to-date
sudo apt-get update

cd ${HOME_DIR}${BASE_DIR_NAME}${GIT_BASE_DIR_NAME} || exit

git update-index -q --refresh
CHANGED=$(git diff-index --name-only HEAD --)
if [ -n "$CHANGED" ]; then
  echo
  echo "
         _
        | |
        | |
        |_|
        (_)"
  echo
  echo "It looks like you have made changes to the original code base"
  echo "You will lose those changes if you update"
  echo -n "Continue anyways? [y/n]"
  read -r answer
  if [ "$answer" != "${answer#[Nn]}" ] ;then
    echo
    echo "Updating Wildlife Cam aborted"
    exit 1
  else
    echo
    echo "Revert local changes"
    git checkout .
  fi
fi

echo "Fetch latest Wildlife Cam version"
git pull --rebase

sudo systemctl restart wildlife-cam
sudo systemctl restart wildlife-cam-web

echo
echo "DONE. You are up-to-date again!"
echo "Find more information on the github account:"
echo "https://github.com/SteffiPeTaffy/wildlife-cam"
echo ""
