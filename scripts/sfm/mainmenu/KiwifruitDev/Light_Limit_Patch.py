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

virtual_alloc = ctypes.windll.kernel32.VirtualAlloc


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


class ICvar(ctypes.Structure):
    _fields_ = [
        ("char_pad", c_char_buf(64)),
        ("FindVar", ctypes.c_void_p),
    ]


class ConVar(ctypes.Structure):
    _fields_ = [
        ("char_pad_01", c_char_buf(12)),
        ("name", ctypes.c_char_p),
        ("char_pad_02", c_char_buf(16)),
        ("default_value", ctypes.c_char_p),
        ("value", ctypes.c_char_p),
    ]


def thiscall(func, restype, arg_types, this, *args):
    buf = virtual_alloc(0, 4096, 0x3000, 0x40)
    code = "\x8b\x4c\x24\x08\x8f\x44\x24\x04\xc3"
    ctypes.memmove(buf, code, len(code))

    return ctypes.WINFUNCTYPE(restype, ctypes.c_void_p, ctypes.c_void_p, *arg_types)(buf)(func, this, *args)


def get_cvar_value(name):
    interface_ptr = ctypes.c_void_p.from_address(ctypes.windll.vstdlib.CreateInterface('VEngineCvar007'))
    interface = ICvar.from_address(interface_ptr.value)

    cvar_ptr = thiscall(interface.FindVar, ctypes.c_int, (ctypes.c_char_p,), ctypes.byref(interface_ptr), name)

    if cvar_ptr:
        cvar_obj = ConVar.from_address(cvar_ptr)

        log.debug('Current value of {} is {}'.format(name, cvar_obj.value))

        return cvar_obj.value


def apply_patches(new_light_limit):
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

    actual_shadow_res = get_cvar_value('r_flashlightdepthres')

    sfmApp.ExecuteGameCommand('r_flashlightdepthres 1024')  # tricksta, force InitDepthTextureShadows()
    QtCore.QTimer.singleShot(25, lambda: sfmApp.ExecuteGameCommand('r_flashlightdepthres {}'.format(actual_shadow_res)))  # revert

    log.debug('Patch applied!')


def get_current_light_limit():
    baseifm = ctypes.windll.ifm._handle + 0xC00  # game/bin/tools/ifm.dll
    find_address = baseifm + 0x27BE2E
    light_limit = mread(find_address, 1)
    return struct.unpack('B', light_limit)[0]


class PatchDialog(QtGui.QDialog):
    def __init__(self):
        super(PatchDialog, self).__init__()
        # Get light limit value
        light_limit_patch_value = get_current_light_limit()
        # User input
        self.light_limit = QtGui.QInputDialog.getInt(self, 'Light Limit', 'Enter a value from 0 to 127 (default: 8)', light_limit_patch_value, 0, 127, 1)
        # Apply patches
        apply_patches(self.light_limit[0])


PatchDialog().show()
