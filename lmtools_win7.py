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


from lmtools_base import LmToolsBase
import sys, os, re


class LmToolsWin7(LmToolsBase):

    """ LmToolsWin7 supports mbed enabled platforms detection across Windows7 OS family
    """
    def __init__(self):
        LmToolsBase.__init__(self)
        self.os_supported.append('Windows7')
        if sys.version_info[0] < 3:
            import _winreg as winreg
        else:
            import winreg
        self.winreg = winreg
        
    """Returns connected mbeds as an mbeds dictionary
    """
    def list_mbeds(self, manufact_ids={}):
        mbeds = []
        for mbed in self.discover_connected_mbeds(manufact_ids):
            d = {}
            if mbed[0]:
                d['mount_point'] = mbed[0]
            else:
                d['mount_point'] = None
            if mbed[1]:
                d['target_id'] = mbed[1]
            else:
                d['target_id'] = None
            if mbed[2]:
                d['serial_port'] = mbed[2]
            else:
                d['serial_port'] = None
            if mbed[0]:
                d['platform_name'] = mbed[3]
            else:
                d['platform_name'] = None
            mbeds += [d]
        return mbeds

    """Returns [(<mbed_mount_point>, <mbed_id>, <com port>, <board model>), ..]
      (notice that this function is permissive: adds new elements in-places when and if found)
    """
    def discover_connected_mbeds(self, defs={}):
        mbeds = [(m[0], m[1], None, None) for m in self.get_connected_mbeds()]
        for i in range(len(mbeds)):
            mbed = mbeds[i]
            mnt, mbed_id = mbed[0], mbed[1]
            mbed_id_prefix = mbed_id[0:4]
            if mbed_id_prefix in defs:
                board = defs[mbed_id_prefix]
                mbeds[i] = (mnt, mbed_id, mbeds[i][2], board)
            port = self.get_mbed_com_port(mbed_id)
            if port:
                mbeds[i] = (mnt, mbed_id, port, mbeds[i][3])
        return mbeds

    """(This goes through a whole new loop, but this assures that even if
        com is not detected, we still get the rest of info like mount point etc.)
    """
    def get_mbed_com_port(self, id):
        self.winreg.Enum = self.winreg.OpenKey(self.winreg.HKEY_LOCAL_MACHINE, 'SYSTEM\CurrentControlSet\Enum')
        usb_devs = self.winreg.OpenKey(self.winreg.Enum, 'USB')

        # first try to find all devs keys (by id)
        dev_keys = []
        for vid in self.iter_keys(usb_devs):
            try:
                dev_keys += [self.winreg.OpenKey(vid, id)]
            except:
                pass

        # then try to get port directly from "Device Parameters"
        for key in dev_keys:
            try:
                param = self.winreg.OpenKey(key, "Device Parameters")
                port = self.winreg.QueryValueEx(param, 'PortName')[0]
                return port
            except:
                pass

        # else follow symbolic dev links in registry
        for key in dev_keys:
            try:
                ports = []
                parent_id = self.winreg.QueryValueEx(key, 'ParentIdPrefix')[0]
                for VID in self.iter_keys(usb_devs):
                    for dev in self.iter_keys_as_str(VID):
                        if parent_id in dev:
                            ports += [self.get_mbed_com_port(dev)]
                for port in ports:
                    if port:
                        return port
            except:
                pass

    """ Returns [(<mbed_mount_point>, <mbed_id>), ..]
    """
    def get_connected_mbeds(self):
        return [m for m in self.get_mbeds() if os.path.exists(m[0])]

    """ Returns [(<mbed_mount_point>, <mbed_id>), ..]
    """
    def get_mbeds(self):
        mbeds = []
        for mbed in self.get_mbed_devices():
            mountpoint = re.match('.*\\\\(.:)$', mbed[0]).group(1)
            # id is a hex string with 10-36 chars
            id = re.search('[0-9A-Fa-f]{10,36}', mbed[1]).group(0)
            mbeds += [(mountpoint, id)]
        return mbeds
    
    
    
    
    # =============================== Registry ====================================
    
    """ Iterate over subkeys of a key returning subkey as string
    """
    def iter_keys_as_str(self, key):
        for i in range(self.winreg.QueryInfoKey(key)[0]):
            yield self.winreg.EnumKey(key, i)

    """ Iterate over subkeys of a key
    """
    def iter_keys(self, key):
        for i in range(self.winreg.QueryInfoKey(key)[0]):
            yield self.winreg.OpenKey(key, self.winreg.EnumKey(key, i))

    """ Iterate over values of a key
    """
    def iter_vals(self, key):
        for i in range(self.winreg.QueryInfoKey(key)[1]):
            yield self.winreg.EnumValue(key, i)

    """ Get MBED devices (connected or not)
    """
    def get_mbed_devices(self):
        return [d for d in self.get_dos_devices() if 'VEN_MBED' in d[1].upper()]

    """ Get DOS devices (connected or not)
    """
    def get_dos_devices(self):
        ddevs = [dev for dev in self.get_mounted_devices() if 'DosDevices' in dev[0]]
        return [(d[0], self.regbin2str(d[1])) for d in ddevs]

    """ Get all mounted devices (connected or not)
    """
    def get_mounted_devices(self):
        devs = []
        mounts = self.winreg.OpenKey(self.winreg.HKEY_LOCAL_MACHINE, 'SYSTEM\MountedDevices')
        for i in range(self.winreg.QueryInfoKey(mounts)[1]):
            devs += [self.winreg.EnumValue(mounts, i)]
        return devs

    """ Decode registry binary to readable string
    """
    def regbin2str(self, bin):
        string = ''
        for i in range(0, len(bin), 2):
            # bin[i] is str in Python2 and int in Python3
            if isinstance(bin[i], int):
                if bin[i] < 128:
                    string += chr(bin[i])
            elif isinstance(bin[i], str):
                string += bin[i]
            else:
                print("ERROR: Can't decode REG_BIN from registry")
                exit(1)
        return string
