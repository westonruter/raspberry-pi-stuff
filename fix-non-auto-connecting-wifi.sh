#!/bin/bash
# Props http://unix.stackexchange.com/questions/93063/i-always-need-to-ifdown-ifup-wlan0-after-reboot

if [ ! -e /home/pi ]; then
    echo "Only run this on your pi."
    exit 1
fi
if [ "$(id -u)" != "0" ]; then
	echo "This script must be run as root" 1>&2
	exit 1
fi

if [ ! -e /usr/local/bin/wifi-reboot ]; then
	echo -n "#!/usr/bin/bash\nifdown wlan0\nifup wlan0" > /usr/local/bin/wifi-reboot
	chmod +x /usr/local/bin/wifi-reboot
fi

if ! grep -q 'wifi-reboot' /etc/network/interfaces; then
	echo "post-up /usr/local/bin/wifi-reboot" >> /etc/network/interfaces
fi
