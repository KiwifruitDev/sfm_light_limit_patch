#   _______                                                                 _                   _                                 _     _   _           _       _           _      __  __   ___     ___     __       __   ___    ______  __  
#  |__   __|                                                               | |                 | |                               | |   | | (_)         | |     | |         | |    / / /_ | |__ \   / _ \    \ \     /_ | |__ \  |____  | \ \ 
#     | |      ___     ___      _ __ ___     __ _   _ __    _   _     ___  | |__     __ _    __| |   ___   __      __   ___    __| |   | |  _    __ _  | |__   | |_   ___  | |   | |   | |    ) | | (_) |    \ \     | |    ) |     / /   | |
#     | |     / _ \   / _ \    | '_ ` _ \   / _` | | '_ \  | | | |   / __| | '_ \   / _` |  / _` |  / _ \  \ \ /\ / /  / _ \  / _` |   | | | |  / _` | | '_ \  | __| / __| | |   | |   | |   / /   > _ <      > >    | |   / /     / /    | |
#     | |    | (_) | | (_) |   | | | | | | | (_| | | | | | | |_| |   \__ \ | | | | | (_| | | (_| | | (_) |  \ V  V /  |  __/ | (_| |   | | | | | (_| | | | | | | |_  \__ \ |_|   | |   | |  / /_  | (_) |    / /     | |  / /_    / /     | |
#     |_|     \___/   \___/    |_| |_| |_|  \__,_| |_| |_|  \__, |   |___/ |_| |_|  \__,_|  \__,_|  \___/    \_/\_/    \___|  \__,_|   |_| |_|  \__, | |_| |_|  \__| |___/ (_)   | |   |_| |____|  \___/    /_/      |_| |____|  /_/      | |
#                                                            __/ |                                                                               __/ |                            \_\                                                    /_/ 
#                                                           |___/                                                                               |___/                                                                                        
# SFM Light Limit Patch Script by KiwifruitDev - Version 1
# This script allows you to change the light limit in SFM.
# https://github.com/KiwifruitDev/sfm_light_limit_patch
#
# Derived from the Directional Scale Controls script by LLIoKoJIad (kumfc/umfc) and Unknown Soldier:
# https://github.com/kumfc/sfm-tools
# https://steamcommunity.com/sharedfiles/filedetails/?id=2942912893
#
# Enjoy!

import ctypes
import struct
import math
from PySide import *

try:
    sfm
except NameError:
    from sfm_runtime_builtins import *


class Log():
    @staticmethod
    def info(msg):
        sfm.Msg('[Python] [*] ' + str(msg) + '\n')

    @staticmethod
    def debug(msg):
        if debug:
            sfm.Msg('[Python] [DEBUG] ' + str(msg) + '\n')


debug = True
log = Log()
w = QtGui.QMainWindow()

read_process_memory = ctypes.windll.kernel32.ReadProcessMemory
write_process_memory = ctypes.windll.kernel32.WriteProcessMemory
get_current_process = ctypes.windll.kernel32.GetCurrentProcess
virtual_protect = ctypes.windll.kernel32.VirtualProtect


def mread(addr, length):
    to = ctypes.create_string_buffer(length)
    data = ctypes.c_size_t()
    read_process_memory(get_current_process(), addr, to, length, ctypes.byref(data))
    return ctypes.string_at(to, length)


def mwrite(addr, data):
    if debug:
        data_str = ' '.join('{:02x}'.format(x) for x in bytearray(data)).upper()
        log.debug('Writing "{}" to {}'.format(data_str, hex(addr)))

    patch = c_char_buf(len(data)).from_buffer(bytearray(data))

    bytes_to_write = ctypes.sizeof(patch)
    bytes_written = ctypes.c_size_t(0)

    write_process_memory(get_current_process(), addr, get_addr(patch), bytes_to_write, ctypes.byref(bytes_written))


def no_permission_mwrite(addr, data):
    old_protect = ctypes.c_ulong()
    virtual_protect(addr, len(data), 0x40, ctypes.byref(old_protect))
    mwrite(addr, data)
    virtual_protect(addr, len(data), old_protect, ctypes.byref(old_protect))


def get_addr(obj):
    if type(obj) == ctypes.c_char_p:
        return ctypes.c_void_p.from_buffer(obj).value
    else:
        return ctypes.addressof(obj)


def c_char_buf(l):
    return ctypes.c_char * l


def apply_patches(new_light_limit, flashlight_depth_res = 2048):
    if new_light_limit < 0:
        new_light_limit = 0

    if new_light_limit > 127:
        new_light_limit = 127

    log.info('Applying patches...')

    baseifm = ctypes.windll.ifm._handle + 0xC00  # game/bin/tools/ifm.dll
    baseclient = ctypes.windll.client._handle + 0xC00  # game/tf/bin/client.dll
    ifm_patch_locations = [baseifm + 0x27BE2E, baseifm + 0x27BEA1, baseifm + 0x27BEA5]
    client_patch_locations = [baseclient + 0xB21E3, baseclient + 0xC214A]

    for patch_location in ifm_patch_locations:
        no_permission_mwrite(patch_location, struct.pack('B', new_light_limit))

    for patch_location in client_patch_locations:
        no_permission_mwrite(patch_location, struct.pack('B', new_light_limit - 1))

    sfmApp.ExecuteGameCommand('r_flashlightdepthres 1024')  # tricksta, force InitDepthTextureShadows()
    QtCore.QTimer.singleShot(25, lambda: sfmApp.ExecuteGameCommand('r_flashlightdepthres {}'.format(flashlight_depth_res))) # revert

    log.debug('Patch applied!')


def get_current_light_limit():
    baseifm = ctypes.windll.ifm._handle + 0xC00  # game/bin/tools/ifm.dll
    find_address = baseifm + 0x27BE2E
    light_limit = mread(find_address, 1)
    return struct.unpack('B', light_limit)[0]


global flashlight_depth_res_value_global
globals().setdefault('flashlight_depth_res_value_global', 2048)


class PatchDialog(QtGui.QDialog):
    def __init__(self):
        super(PatchDialog, self).__init__()
        # Set title
        self.setWindowTitle('Light Limit')
        # Variables
        light_limit_patch_value = get_current_light_limit()
        self.flashlight_depth_res_value = globals()['flashlight_depth_res_value_global']
        if self.flashlight_depth_res_value == 0 or self.flashlight_depth_res_value == None:
            self.flashlight_depth_res_value = 2048
        # Widgets
        self.form = QtGui.QFormLayout(self)
        self.light_limit_label = QtGui.QLabel('Enter the new max shadowed light value from 0 to 127:')
        self.light_limit = QtGui.QSpinBox()
        self.light_limit.setRange(0, 127)
        self.light_limit.setValue(light_limit_patch_value)
        self.light_limit.setSingleStep(1)
        self.flashlight_depth_res_label = QtGui.QLabel('Enter the current -sfm_shadowmapres value (if present in launch options):')
        self.flashlight_depth_res = QtGui.QSpinBox()
        self.flashlight_depth_res.setRange(1, 8192)
        self.flashlight_depth_res.setValue(self.flashlight_depth_res_value)
        self.flashlight_depth_res.setSingleStep(1)
        self.info1 = QtGui.QLabel('Using high max shadowed light values with high -sfm_shadowmapres values can cause SFM to crash.')
        self.info2 = QtGui.QLabel('Make sure you save before using! Try using a lower -sfm_shadowmapres value if SFM crashes.')
        self.info3 = QtGui.QLabel('A sane max shadowed light value is 24, but higher options are available for experimentation.')
        self.info4 = QtGui.QLabel('Please ensure the -sfm_shadowmapres value is correct, as otherwise SFM will run very slowly.')
        self.buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel, QtCore.Qt.Horizontal, self)
        # Add widgets
        self.form.addRow(self.light_limit_label, self.light_limit)
        self.form.addRow(self.flashlight_depth_res_label, self.flashlight_depth_res)
        self.form.addRow(QtGui.QLabel(''))
        self.form.addRow(self.info1)
        self.form.addRow(self.info2)
        self.form.addRow(self.info3)
        self.form.addRow(QtGui.QLabel(''))
        self.form.addRow(self.info4)
        self.form.addRow(QtGui.QLabel(''))
        self.form.addRow(self.buttons)
        # Connect
        self.flashlight_depth_res.valueChanged.connect(self.flashlight_depth_res_changed)
        self.buttons.accepted.connect(self.apply)
        self.buttons.rejected.connect(self.close)
    def apply(self):
        # Apply patches
        apply_patches(self.light_limit.value(), self.flashlight_depth_res_value)
        # Set global flashlight_depth_res_value
        globals()['flashlight_depth_res_value_global'] = self.flashlight_depth_res_value
        # Close dialog
        self.close()
    def flashlight_depth_res_changed(self, value):
        # Round up to the nearest power of 2 if value is greater than current
        if value > self.flashlight_depth_res_value:
            value = 2 ** (value - 1).bit_length()
            self.flashlight_depth_res_value = value
            self.flashlight_depth_res.setValue(value)
        # Round down to the nearest power of 2 if value is less than current
        elif value < self.flashlight_depth_res_value:
            round = 2 ** (value - 1).bit_length()
            if round > value:
                round /= 2
            self.flashlight_depth_res_value = round
            self.flashlight_depth_res.setValue(round)


PatchDialog().exec_()
