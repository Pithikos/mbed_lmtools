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

class LmToolsBase:
    """ Base class for lmtools used by test suite
    """
    def __init__(self):
        """ ctor
        """
        pass

    # Which OSs are supported by this module
    # Note: more than one OS can be supported by lmtools_* module
    os_supported = []

    # Dictionary describing mapping between manufacturers' ids and platform name.
    manufacture_ids = {}

    # Interface
    def list_mbeds(self):
        """ Gets information about mbeds connected to device

        MBED_BOARD
        {
            'mount_point' : <>,
            'serial_port' : <>,
            'target_id' : <>,
            'platform_name' : <>,
        }
        # If field unknown, place None

        @return MBED_BOARDS = [ <MBED_BOARD>, ]

        """
        return None

    # Private part, methods used to drive interface functions
    def load_mbed_description(self, file_name):
        """ Loads JSON file with mbeds' description (mapping between target id and platform name)
            Sets self.manufacture_ids with mapping between manufacturers' ids and platform name.
        """
        self.manufacture_ids = {}   # TODO: load this values from file
        pass

    def err(self, text):
        """ Prints error messages
        """
        print text

    # Private functions supporting API

    def get_json_data_from_file(json_spec_filename, verbose=False):
        """ Loads from file JSON formatted string to data structure
            @return None if JSON can be loaded
        """
        result = None
        try:
            with open(json_spec_filename) as data_file:
                try:
                    result = json.load(data_file)
                except ValueError as json_error_msg:
                    result = None
                    print "Error parsing TID file(%s): %s" % (json_spec_filename, json_error_msg)
        except IOError as fileopen_error_msg:
            print "Warning: %s" % (fileopen_error_msg)
        return result
