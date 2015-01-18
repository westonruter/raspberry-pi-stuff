#!/usr/bin/env python
# raspi-address-list
# Copyright (C) 2015  Weston Ruter
# Weston Ruter (@westonruter)
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

'''
List the ipv4 and mac addresses for Raspberry Pi devices connected on the current network
'''


import subprocess
import math
import os
import argparse
import sys
import re
import pprint
import xml.etree.ElementTree as ET

class RaspiAddressList:

    @classmethod
    def parse_args(cls, argv):
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=__doc__
        )
        args = parser.parse_args(argv)
        return args


    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)
        self.self_dir = os.path.dirname(os.path.realpath(__file__))
        self.subnet_range = self.get_subnet_range()
        self.all_hosts = self.get_nmap_hosts(self.subnet_range)
        self.pi_hosts = self.filter_pi_hosts(self.all_hosts)
        if len(self.pi_hosts) == 0:
            raise Exception('No hosts found')
        
    def get_subnet_range(self):
        script = os.path.join( self.self_dir, 'subnet-range.sh' )
        return subprocess.check_output([script]).strip()
    
    def get_nmap_hosts(self, subnet_range):
        xml = subprocess.check_output(['sudo', 'nmap', '-sn', '-oX', '-', subnet_range])
        root = ET.fromstring(xml)
        hosts = []
        for host_el in root.iter('host'):
            host = {
                'status': host_el.find('status').attrib,
                'hostnames': [hostame_el.attrib for hostname_el in host_el.findall('hostname')],
                'addresses': [address_el.attrib for address_el in host_el.findall('address')]
            }
            hosts.append(host)
        return hosts

    def filter_pi_hosts(self, hosts):
        pi_hosts = []
        for host in hosts:
            is_pi = False
            addrtypes = set()
            for address in host.get('addresses'):
                addrtypes.add(address.get('addrtype'))
                if 'raspberry' in address.get('vendor', '').lower():
                    is_pi = True
            if is_pi and 'ipv4' in addrtypes:
                pi_hosts.append(host)
        return pi_hosts
    
    def get_mac_ipv4_tuples(self, hosts):
        tuples = []
        for pi_host in app.pi_hosts:
            ipv4 = None
            mac = None
            for addr in pi_host.get('addresses'):
                if addr.get('addrtype') == 'ipv4':
                    ipv4 = addr.get('addr')
                    break
            for addr in pi_host.get('addresses'):
                if addr.get('addrtype') == 'mac':
                    mac = addr.get('addr')
                    break
            tuples.append(( ipv4, mac ))
        return tuples

if __name__ == '__main__':
    try:
        args = RaspiAddressList.parse_args(sys.argv[1:])
        kwargs = args.__dict__
        app = RaspiAddressList( **kwargs )
        for ipv4, mac in app.get_mac_ipv4_tuples(app.pi_hosts):
            print "%s\t%s" % ( ipv4 or '', mac or '' )

    except Exception as e:
        sys.stderr.write( str(e) + "\n" )
        sys.exit(1)
