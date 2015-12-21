# Setup Instructions

## Write the latest Raspbian OS to an SD Card

1. Put your SD card into your card reader.
2. Run `python raspi-diskutil.py` and enter `y` to confirm the selected disk and image.
3. Put disk into the Pi.

## Set up a Pi with a new card

1. Connect Pi to Ethernet
2. Connect power.
3. Ensure that your Pi is connected to the network by seeing it listed via `python raspi-address-list.py`
4. Add your SSH key to the Raspberry Pi(s) on your network and set their hostnames via `bash raspi-ssh-config.sh`
5. Reserve the IP address currently assigned to your Pi's MAC address from previous step in your router's configuration.

The following commands are all executed while SSH'ed into your Pi:

1. Set your password over SSH: `passwd` and `sudo passwd root`
2. Turn off SSH password authentication: `sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config; sudo /etc/init.d/ssh restart`
3. Expand root filesystem over SSH: `sudo raspi-config  --expand-rootfs; sudo shutdown -r now`. Then re-SSH to the Pi.
4. `raspi-config`, Internationalisation Options, Change Locale: Set locale to `en_US.UTF-8 UTF-8`, including default locale for system environment
5. `raspi-config`, Internationalisation Options, Change Timezone: Set as `America/Los_Angeles`
6. `raspi-config`, Internationalisation Options, Keyboard Layout
7. `raspi-config`, Enable Camera Support
8. Update system: `sudo apt-get update && sudo apt-get upgrade -y`
9. Install stuff: `sudo apt-get install -y ca-certificates screen nginx rpi-update`
10. Update the firmware: `sudo rpi-update; sudo shutdown -r now`
11. Given a Pi that has a hostname `raspberrypi-12345678`, set up WiFi via: `scp raspi-wifi.sh raspberrypi-12345678:~ && ssh raspberrypi-12345678 "sudo ~/raspi-wifi.sh $ssid $passphrase"` (supply your SSID and passphrase in place of the variables)
12. Check for IP and MAC address associated with WiFi interface, and reserve the IP address currently assigned to your Pi's MAC address from previous step in your router's configuration.
13. Shutdown, turn off, unplug from Ethernet, and then boot without Ethernet.
14. Install auto-update monthly cronjob via `crontab -e` and add the following line: `0 0 0 * * ( apt-get update && apt-get dist-upgrade -y && ( if command -v rpi-update; then sudo rpi-update; fi ) && /sbin/shutdown -r now ) > /dev/null 2>&1`

## Configure Firewall

```bash
sudo iptables -A INPUT -j ACCEPT -m state --state ESTABLISHED,RELATED
sudo iptables -A INPUT -p tcp --dport 22 -m state --state NEW -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 80 -m state --state NEW -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -m state --state NEW -j ACCEPT
sudo iptables -A INPUT -p icmp -m icmp --icmp-type 8 -j ACCEPT
sudo iptables -P INPUT DROP
```

# Credits

By [Weston Ruter](https://weston.ruter.net/). GPLv2 license.