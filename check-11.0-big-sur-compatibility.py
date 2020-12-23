#!/usr/bin/env python
# encoding: utf-8

# ================================================================================
# check-11.0-big-sur-compatibility.py
#
# This script checks if the current system is compatible with macOS 11.0 Big Sur.
# These checks are based on the installCheckScript and volCheckScript in
# formerly found in the distribution file of OSInstall.mpkg installer package.

# The OSInstall.mpkg could be found in the Packages directory of InstallESD disk image:
#   /Applications/Install macOS Catalina.app/Contents/SharedSupport/InstallESD.dmg
#       -> /Volumes/InstallESD/Packages/OSInstall.mpkg
#
# This disk image no longer seems to exist, starting with macOS 11.0 Big Sur.
#
# A list of supported Device/Board IDs can be found within the macOS 11.0 Installer:
# /Applications/Install macOS Big Sur.app/Contents/SharedSupport/SharedSupport.dmg
# Then, inside the .dmg:
# com_apple_MobileAsset_MacSoftwareUpdate/com_apple_MobileAsset_MacSoftwareUpdate.xml
#
# There is also a JSON file in the above directory, whose contents may be easier 
# to copy into Python.
#
# The checks done by this script are (in order):
# - Machine is a virtual machine or has a specific supported board-id
# - Machine model is not in a list of unsupported models
# - Current system version is less than 11.0 (10.16) and at least 10.9
#
# Exit codes:
# 0 = Big Sur is supported
# 1 = Big Sur is not supported
#
#
# Jacob Burley <j@jc0b.computer>
# https://github.com/jc0b/adminscripts
#
# Thanks to Hannes Juutilainen, Graham Pugh, Ralph Cyranka, Ed Bobak and @tcinbis
#
# ================================================================================

import sys
import subprocess
import os
import re
import plistlib
from distutils.version import StrictVersion


# ================================================================================
# Start configuration
# ================================================================================

# Set this to False if you don't want any output, just the exit codes
verbose = True

# Set this to True if you want to add "bigsur_supported" custom conditional to
# /Library/Managed Installs/ConditionalItems.plist
update_munki_conditional_items = False

# ================================================================================
# End configuration
# ================================================================================


def logger(message, status, info):
    if verbose:
        print "%14s: %-40s [%s]" % (message, status, info)
    pass


def conditional_items_path():
    # <https://github.com/munki/munki/wiki/Conditional-Items>
    # Read the location of the ManagedInstallDir from ManagedInstall.plist
    
    cmd = [
        "/usr/bin/defaults",
        "read",
        "/Library/Preferences/ManagedInstalls",
        "ManagedInstallDir"
    ]
    p = subprocess.Popen(cmd, bufsize=1, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (results, err) = p.communicate()
    managed_installs_dir = results.strip()
    
    # Make sure we're outputting our information to "ConditionalItems.plist"
    if managed_installs_dir:
        return os.path.join(managed_installs_dir, 'ConditionalItems.plist')
    else:
        # Munki default
        return "/Library/Managed Installs/ConditionalItems.plist"


def munki_installed():
    cmd = ["pkgutil", "--pkg-info", "com.googlecode.munki.core"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = p.communicate()[0]
    if p.returncode == 0:
        return True
    else:
        return False


def is_system_version_supported():
    system_version_plist = plistlib.readPlist("/System/Library/CoreServices/SystemVersion.plist")
    product_name = system_version_plist['ProductName']
    product_version = system_version_plist['ProductVersion']
    if StrictVersion(product_version) >= StrictVersion('10.16'):
        logger("System",
               "%s %s" % (product_name, product_version),
               "Failed")
        return False
    elif StrictVersion(product_version) >= StrictVersion('10.9'):
        logger("System",
               "%s %s" % (product_name, product_version),
               "OK")
        return True
    else:
        logger("System",
               "%s %s" % (product_name, product_version),
               "Failed")
        return False


def get_board_id():
    """Gets the local device ID on Apple Silicon Macs or the board_id of older Macs"""
    ioreg_cmd = ["/usr/sbin/ioreg", "-c", "IOPlatformExpertDevice", "-d", "2"]
    try:
        ioreg_output = subprocess.check_output(ioreg_cmd).splitlines()
        board_id = ""
        device_id = ""
        for line in ioreg_output:
            line_decoded = line.decode("utf8")
            if "board-id" in line_decoded:
                board_id = line_decoded.split("<")[-1]
                board_id = board_id[
                    board_id.find('<"') + 2 : board_id.find('">')  # noqa: E203
                ]
            elif "compatible" in line_decoded:
                device_details = line_decoded.split("<")[-1]
                device_details = device_details[
                    device_details.find("<")
                    + 2 : device_details.find(">")  # noqa: E203
                ]
                device_id = (
                    device_details.replace('","', ";").replace('"', "").split(";")[0]
                )
        if board_id:
            return board_id
        elif device_id:
            return device_id
    except subprocess.CalledProcessError as err:
        raise ReplicationError(err)


def is_virtual_machine():
    cmd = ["/usr/sbin/sysctl", "-n", "machdep.cpu.features"]
    p = subprocess.Popen(cmd, bufsize=1, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (results, err) = p.communicate()
    for feature in results.split():
        if feature == "VMM":
            logger("Board ID",
                   "Virtual machine",
                   "OK")
            return True
    return False


def get_current_model():
    cmd = ["/usr/sbin/sysctl", "-n", "hw.model"]
    p = subprocess.Popen(cmd, bufsize=1, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (results, err) = p.communicate()
    return results.strip()


def is_supported_model():
    non_supported_models = [
        'iMac4,1',
        'iMac4,2',
        'iMac5,1',
        'iMac5,2',
        'iMac6,1',
        'iMac7,1',
        'iMac8,1',
        'iMac9,1',
        'iMac10,1',
        'iMac11,1',
        'iMac11,2',
        'iMac11,3',
        'iMac12,1',
        'iMac12,2',
        'iMac13,1',
        'iMac13,2',
        'iMac14,1',
        'iMac14,2',
        'MacBook1,1',
        'MacBook2,1',
        'MacBook3,1',
        'MacBook4,1',
        'MacBook5,1',
        'MacBook5,2',
        'MacBook6,1',
        'MacBook7,1',
        'MacBookAir1,1',
        'MacBookAir2,1',
        'MacBookAir3,1',
        'MacBookAir3,2',
        'MacBookAir4,1',
        'MacBookAir4,2',
        'MacBookAir5,1',
        'MacBookAir5,2',
        'MacBookPro1,1',
        'MacBookPro1,2',
        'MacBookPro2,1',
        'MacBookPro2,2',
        'MacBookPro3,1',
        'MacBookPro4,1',
        'MacBookPro5,1',
        'MacBookPro5,2',
        'MacBookPro5,3',
        'MacBookPro5,4',
        'MacBookPro5,5',
        'MacBookPro6,1',
        'MacBookPro6,2',
        'MacBookPro7,1',
        'MacBookPro8,1',
        'MacBookPro8,2',
        'MacBookPro8,3',
        'MacBookPro9,1',
        'MacBookPro9,2',
        'MacBookPro10,1',
        'MacBookPro10,2',
        'Macmini1,1',
        'Macmini2,1',
        'Macmini3,1',
        'Macmini4,1',
        'Macmini5,1',
        'Macmini5,2',
        'Macmini5,3',
        'Macmini6,1',
        'Macmini6,2',
        'MacPro1,1',
        'MacPro2,1',
        'MacPro3,1',
        'MacPro4,1',
        'MacPro5,1',
        'Xserve1,1',
        'Xserve2,1',
        'Xserve3,1',
        ]
    current_model = get_current_model()
    if current_model in non_supported_models:
        logger("Model",
               "\"%s\" is not supported" % current_model,
               "Failed")
        return False
    else:
        logger("Model",
               current_model,
               "OK")
        return True


def is_supported_board_id():
    platform_support_values = [
    'J132AP',
    'J137AP',
    'J140AAP',
    'J140KAP',
    'J152FAP',
    'J160AP',
    'J174AP',
    'J185AP',
    'J185FAP',
    'J213AP',
    'J214KAP',
    'J215AP',
    'J223AP',
    'J230KAP',
    'J680AP',
    'J780AP',
    'X589AMLUAP',
    'X589ICLYAP',
    'X86LEGACYAP',
    'J273aAP',
    'J273AP',
    'J274AP',
    'J293AP',
    'J313AP',
    'T485AP',
    'Mac-06F11F11946D27C5',
    'Mac-06F11FD93F0323C5',
    'Mac-0CFF9C7C2B63DF8D',
    'Mac-112818653D3AABFC',
    'Mac-112B0A653D3AAB9C',
    'Mac-189A3D4F975D5FFC',
    'Mac-1E7E29AD0135F9BC',
    'Mac-226CB3C6A851A671',
    'Mac-27AD2F918AE68F61',
    'Mac-2BD1B31983FE1663',
    'Mac-35C1E88140C3E6CF',
    'Mac-35C5E08120C7EEAF',
    'Mac-36B6B6DA9CFCD881',
    'Mac-3CBD00234E554E41',
    'Mac-42FD25EABCABB274',
    'Mac-473D31EABEB93F9B',
    'Mac-4B682C642B45593E',
    'Mac-50619A408DB004DA',
    'Mac-53FDB3D8DB8CA971',
    'Mac-551B86E5744E2388',
    'Mac-564FBA6031E5946A',
    'Mac-5A49A77366F81C72',
    'Mac-5F9802EFE386AA28',
    'Mac-63001698E7A34814',
    'Mac-65CE76090165799A',
    'Mac-66E35819EE2D0D05',
    'Mac-6FEBD60817C77D8A',
    'Mac-747B1AEFF11738BE',
    'Mac-77F17D7DA9285301',
    'Mac-7BA5B2D9E42DDD94',
    'Mac-7BA5B2DFE22DDD8C',
    'Mac-7DF21CB3ED6977E5',
    'Mac-81E3E92DD6088272',
    'Mac-827FAC58A8FDFA22',
    'Mac-827FB448E656EC26',
    'Mac-87DCB00F4AD77EEA',
    'Mac-90BE64C3CB5A9AEB',
    'Mac-937A206F2EE63C01',
    'Mac-937CB26E2E02BB01',
    'Mac-9394BDF4BF862EE7',
    'Mac-9AE82516C7C6B903',
    'Mac-9F18E312C5C2BF0B',
    'Mac-A369DDC4E67F1C45',
    'Mac-A5C67F76ED83108C',
    'Mac-A61BADE1FDAD7B05',
    'Mac-AA95B1DDAB278B95',
    'Mac-AF89B6D9451A490B',
    'Mac-B4831CEBD52A0C4C',
    'Mac-B809C3757DA9BB8D',
    'Mac-BE088AF8C5EB4FA2',
    'Mac-BE0E8AC46FE800CC',
    'Mac-C6F71043CEAA02A6',
    'Mac-CAD6701F7CEA0921',
    'Mac-CF21D135A7D34AA6',
    'Mac-CFF7D910A743CAAF',
    'Mac-DB15BD556843C820',
    'Mac-E1008331FDC96864',
    'Mac-E43C1C25D4880AD6',
    'Mac-E7203C0F68AA0004',
    'Mac-EE2EBD4B90B839A8',
    'Mac-F305150B0C7DEEEF',
    'Mac-F60DEB81FF30ACF6',
    'Mac-FA842E06C61E91C5',
    'Mac-FFE5EF870D7BA81A'
    ]
    board_id = get_board_id()
    if board_id in platform_support_values:
        logger("Board ID",
               board_id,
               "OK")
        return True
    else:
        logger("Board ID",
               "\"%s\" is not supported" % board_id,
               "Failed")
        return False


def append_conditional_items(dictionary):
    current_conditional_items_path = conditional_items_path()
    if os.path.exists(current_conditional_items_path):
        existing_dict = plistlib.readPlist(current_conditional_items_path)
        output_dict = dict(existing_dict.items() + dictionary.items())
    else:
        output_dict = dictionary
    plistlib.writePlist(output_dict, current_conditional_items_path)
    pass


def main(argv=None):
    bigsur_supported_dict = {}

    # Run the checks
    model_passed = is_supported_model()
    board_id_passed = is_supported_board_id()
    system_version_passed = is_system_version_supported()

    if is_virtual_machine():
        bigsur_supported = 0
        bigsur_supported_dict = {'bigsur_supported': True}
    elif model_passed and board_id_passed and system_version_passed:
        bigsur_supported = 0
        bigsur_supported_dict = {'bigsur_supported': True}
    else:
        bigsur_supported = 1
        bigsur_supported_dict = {'bigsur_supported': False}

    # Update "ConditionalItems.plist" if munki is installed
    if munki_installed() and update_munki_conditional_items:
        append_conditional_items(bigsur_supported_dict)

    # Exit codes:
    # 0 = Big Sur is supported
    # 1 = Big Sur is not supported
    return bigsur_supported


if __name__ == '__main__':
    sys.exit(main())