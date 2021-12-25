#!/bin/sh

omxplayer -o local FoxIntro.mp3
cd /home/pi/sound_project/
sudo python3 Record.py
