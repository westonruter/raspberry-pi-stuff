#!/bin/bash
# raspi-ssh-config.sh
# By Weston Ruter (@westonruter)
# Copy SSH public key to all Raspberry Pis found on the network,
# and set hostname with prompt for ssh-config

set -e

cd "$(dirname "$0")"

while read -r ip mac; do
    hyphenated_mac=$( ( sed 's/:/-/g' | tr '[:upper:]' '[:lower:]' ) <<< "$mac")
    
    echo "IP: $ip"
    echo "MAC: $mac"
    echo "Copy ssh key..."
    ssh-copy-id -i "pi@$ip"
    
    pi_hostname=$( cat raspi-hostname.sh | ssh "pi@$ip" 'cat - | bash 2>/dev/null' )
    echo "Device Name: $pi_hostname"
    
    echo "RECOMMENDED: Reserve $ip for MAC $mac in your router, though beware of switching between Ethernet and WiFi"
    echo "If done, then add the following to your ~/.ssh/config:"
    echo "Host $pi_hostname"
    echo "Hostname $ip  # MAC: $mac"
    echo "User pi"
    echo "ForwardAgent yes"
    
done < <(python raspi-address-list.py)
