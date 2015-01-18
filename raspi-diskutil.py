#!/usr/bin/env python
# parse-diskutil-plist
# Copyright (C) 2013  Weston Ruter
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
Write Raspberry Pi disk images to a connected SD card.
'''


import plistlib
import subprocess
import math
import os
import argparse
import sys
import re
import pprint

class RaspiDiskutil:

    max_size = 64000000000 # 64GB, safeguard against selecting non-SD card
    skipped_device_ids = ['disk0']
    latest_disk_image_zip_url = 'http://downloads.raspberrypi.org/raspbian_latest'
    latest_disk_image_zip_path = os.path.dirname(os.path.realpath(__file__)) + '/disk-images/raspbian_latest.zip'

    @classmethod
    def parse_args(cls, argv):
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=__doc__
        )
        parser.add_argument('-i', '--image',
            default=cls.latest_disk_image_zip_path,
            required=False,
            dest='disk_image_zip_path'
        )
        parser.add_argument('-y', '--yes',
            action='store_true',
            help="Auto-accept",
            dest='skip_confirmation'
        )
        args = parser.parse_args(argv)
        return args


    @staticmethod
    def main(args):

        args = RaspiDiskutil.parse_args(args)
        kwargs = args.__dict__
        app = RaspiDiskutil(**kwargs)
        app.select_disk()
        print "Using this disk:"
        pprint.pprint(app.selected_disk)

        print "Unmounting partitions..."
        app.unmount_partitions()

        print "Now can write image to:", app.selected_disk.get('DeviceIdentifier')

        app.fetch_disk_image()
        app.write_disk_image()
        print 'Done!'


    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)
        self.disks_and_partitions = getattr(self.get_diskutil_list(), 'AllDisksAndPartitions')


    def get_diskutil_list(self):
        raw_plist = subprocess.check_output(['diskutil', 'list', '-plist'])
        plist = plistlib.readPlistFromString(raw_plist)
        return plist


    def select_disk(self):
        disks = []

        for disk in self.disks_and_partitions:
            if disk.get('DeviceIdentifier') in self.skipped_device_ids:
                continue
            if disk.get('Size') > self.max_size:
                continue
            if disk.get('MountPoint') == '/':
                continue
            disks.append(disk)

        if len(disks) == 0:
            raise Exception('Unable to find candidate disk')
        if len(disks) > 1:
            raise Exception('Found more than one candidate disk')
        self.selected_disk = disks[0]
        return self.selected_disk


    def unmount_partitions(self):
        unmounted_partitions = []
        if not self.selected_disk.get('Partitions'):
            return unmounted_partition
        for partition in self.selected_disk.get('Partitions'):
            if partition.get('MountPoint'):
                cmd = ['sudo', 'diskutil', 'unmount', '/dev/' + partition.get('DeviceIdentifier')]
                print ' '.join(cmd)
                subprocess.check_call(cmd)
                unmounted_partitions.append(partition)
        return unmounted_partitions


    def fetch_disk_image(self):
        if os.path.exists(self.disk_image_zip_path):
            return
        elif self.latest_disk_image_zip_path == self.disk_image_zip_path:
            print 'Downloading', self.latest_disk_image_zip_url, 'to', self.latest_disk_image_zip_path
            cmd = ['wget', '-O', self.latest_disk_image_zip_path, self.latest_disk_image_zip_url]
            subprocess.check_call(cmd)
        else:
            raise Exception('Supplied disk image is not found: ' + self.disk_image_zip_path)


    def write_disk_image(self):
        unzip_cmd = ['unzip', '-p', self.disk_image_zip_path, '*.img']
        dd_cmd = ['sudo', 'dd', 'bs=1m', 'of=/dev/' + self.selected_disk.get('DeviceIdentifier')]
        print ' '.join(unzip_cmd) + ' | ' + ' '.join(dd_cmd)

        if not self.skip_confirmation:
            print "Proceed? [y/n]:",
            choice = raw_input().lower()
            if choice[0] == 'n':
                print "Aborting"
                sys.exit(0)
            elif choice[0] != 'y':
                raise Exception('Wrong answer')

        print "Writing to disk..."
        p1 = subprocess.Popen(unzip_cmd, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(dd_cmd, stdin=p1.stdout, stdout=subprocess.PIPE)
        p2.communicate()

if __name__ == '__main__':
    RaspiDiskutil.main(sys.argv[1:])
