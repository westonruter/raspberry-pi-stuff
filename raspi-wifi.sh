#!/bin/bash
# raspi-wifi.sh
# Add a WiFi network to a Pi
# By Weston Ruter (@westonruter)
# http://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md

if [ ! -e /home/pi ]; then
    echo "Only run this on your pi."
    exit 1
fi

ssid="$1"
if [ -z "$ssid" ]; then
    echo "Supply SSID as first argument"
    exit 1
fi

password="$2"
if [ -z "$password" ]; then
    echo "Supply password as first argument"
    exit 1
fi

wpa_supplicant_file=/etc/wpa_supplicant/wpa_supplicant.conf

if [ ! -e "$wpa_supplicant_file" ]; then
    sudo touch "$wpa_supplicant_file"
fi

if grep -q "$ssid" "$wpa_supplicant_file"; then
    echo "SSID already added"
else
    echo -e "\nnetwork={\n\tssid=\"$ssid\"\n\tpsk=\"$password\"\n}" | sudo tee -a "$wpa_supplicant_file" > /dev/null
    echo "Added SSID: $ssid"
fi

echo "Rebooting WiFi"
sudo ifdown wlan0
sudo ifup wlan0
