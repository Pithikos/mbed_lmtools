"""
mbed SDK
Copyright (c) 2011-2013 ARM Limited

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import re
import json
import optparse
import subprocess
from prettytable import PrettyTable

from lmtools_base import LmToolsBase


class LmToolsUbuntu(LmToolsBase):
    """ LmToolsUbuntu supports mbed enabled platforms detection across Debian/Ubuntu OS family
    """
    def __init__(self):
        """ ctor
        """
        self.os_supported.append('Ubuntu')
        self.hex_uuid_pattern = "usb-[0-9a-zA-Z_-]*_([0-9a-zA-Z]*)-.*"
        self.name_link_pattern = "(usb-[0-9a-zA-Z_-]*_[0-9a-zA-Z]*-.*$)"
        self.mount_media_pattern = "^/[a-zA-Z0-9/]* on (/[a-zA-Z0-9/]*) "

    def list_mbeds(self):
        result = None
        disk_ids = get_dev_by_id('disk')
        serial_ids = get_dev_by_id('serial')
        mount_ids = get_mounts()

        mbeds = get_(tids, disk_ids, serial_ids, mount_ids)
        orphans = get_not_detected(tids, disk_ids, serial_ids, mount_ids)
        all_devices = mbeds + orphans
        return all_devices
        
    # Private methods

    def get_dev_by_id(subdir):
        """ Lists disk devices by id
            Command: 'ls -oA /dev/disk/by-id/'
        """
        result = []
        cmd = 'ls -oA /dev/' + subdir + '/by-id/'
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p.stdout.readlines():
            # print line,
            result.append(line)
        retval = p.wait()
        return result

    def get_mounts():
        """ Lists mounted devices with vfat file system (potential mbeds)
        """
        result = []
        cmd = 'mount | grep vfat'
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p.stdout.readlines():
            # print line,
            result.append(line)
        retval = p.wait()
        return result

    def get_(tids, disk_list, serial_list, mount_list):
        """ Find all known MBED devices
        """
        # Regular expr. formulas
        hup = re.compile(hex_uuid_pattern)
        nlp = re.compile(name_link_pattern)
        mmp = re.compile(mount_media_pattern)

        # Find for all disk connected all MBED ones we know about from TID list
        disk_hex_ids = get_disk_hex_ids(disk_list)

        # TODO: maybe not needed
        serial_hex_ids = []
        for sl in serial_list:
            m = hup.search(sl)
            if m and len(m.groups()):
                serial_hex_ids.append(m.group(1))

        map_tid_to_mbed = get_tid_mbed_name_remap(tids)
       
        result = []

        # Search if we have 
        for dhi in disk_hex_ids.keys():
            for mttm in map_tid_to_mbed.keys():
                if dhi in mttm:
                    mbed_name = map_tid_to_mbed[mttm]
                    mbed_dev_disk = ""
                    mbed_dev_serial = ""

                    disk_link = disk_hex_ids[dhi]
                    # print "Fount MBED disk: " + disk_link #mbed_name + ": " + mttm + " (" + dhi + ")"
                    mbed_dev_disk = get_dev_name(disk_link) # m.group(1) if m and len(m.groups()) else "unknown"
                    mbed_dev_serial = get_mbed_serial(serial_list, dhi)
                    # Print detected device
                    mbed_mount_point = get_mount_point(mbed_dev_disk, mount_list)
                    if mbed_mount_point and  mbed_dev_serial:
                        result.append([mbed_name, mbed_dev_disk, mbed_mount_point, mbed_dev_serial, disk_hex_ids[dhi]])
        return result

    def get_tid_mbed_name_remap(tids):
        """ Remap to get TID -> mbed name mapping 
        """
        map_tid_to_mbed = {}
        if tids:
            for key in tids:
                for v in tids[key]:
                    map_tid_to_mbed[v] = key
        return map_tid_to_mbed

    def get_not_detected(tids, disk_list, serial_list, mount_list):
        """ Find all unknown mbed enabled devices
        """ 
        map_tid_to_mbed = get_tid_mbed_name_remap(tids)
        orphan_mbeds = []
        for disk in disk_list:
            if "mbed" in disk.lower():
                orphan_found = True
                for tid in map_tid_to_mbed.keys():
                    if tid in disk:
                        orphan_found = False
                        break
                if orphan_found:
                    orphan_mbeds.append(disk)

        # Search for corresponding MBED serial
        disk_hex_ids = get_disk_hex_ids(orphan_mbeds)   

        result = []
        # FInd orphan serial name
        for dhi in disk_hex_ids:
            orphan_serial = get_mbed_serial(serial_list, dhi)
            if orphan_serial:
                orphan_dev_disk = get_dev_name(disk_hex_ids[dhi])
                orphan_dev_serial = "/dev/" + get_dev_name(orphan_serial)
                orphan_mount_point = get_mount_point(orphan_dev_disk, mount_list)
                if orphan_mount_point and orphan_dev_serial:
                    result.append([ "*not detected", orphan_dev_disk, orphan_mount_point, orphan_dev_serial, disk_hex_ids[dhi]])
        return result
















