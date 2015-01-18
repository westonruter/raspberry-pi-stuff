#!/bin/bash
# Output the subnet range for the device on the network
# Known to work on OSX
# By Weston Ruter (@westonruter)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

set -e

subnet_range=''
while IFS=$'\0' read -a line; do
    # start of a new interface
    if grep -qE '^[0-9a-z][0-9a-z]*:' <<< "$line"; then
        current_interface=$(sed 's/:.*//' <<< "$line")
    fi
    
    # skip if current interface not discovered yet
    if [ -z "$current_interface" ]; then
        continue
    fi
    
    # skip if not en0, en1, etc
    if ! grep -qE '^en[0-9]' <<< "$current_interface"; then
        continue
    fi
    
    if ! (grep inet | grep -qv inet6) <<< "$line"; then
        continue
    fi
    subnet_range=$( ( sed 's/.* //' | sed 's/[0-9]*$//' ) <<< "$line" )'0/24'
done < <(ifconfig)

if [ -z "$subnet_range" ]; then
    echo 'Failed to locate IP address via ifconfig' >&2
    exit 1
else
    echo "$subnet_range"
fi
