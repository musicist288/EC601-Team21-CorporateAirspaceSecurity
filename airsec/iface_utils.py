"""
This module provides utilities to bring up and configure
WiFi interfaces. Currently the only supported platform
is Linux environments that have the `ip` and `iw` commands
installed.

The process running these functions must have sufficient
privileges to perform network configuration commands.
"""

from dataclasses import dataclass
from functools import wraps
from typing import List, Union
import os
import re
import shutil
import subprocess

exe_paths = {
    "ip": [
        "/usr/sbin/ip"
    ],
    "iw": [
        "/usr/sbin/iw"
    ]
}

@dataclass
class InterfaceConfig:
    name: str
    ifindex: str = ''
    wdev: int = 0
    addr: str = ''
    type: str = ''
    power: str = ''


def get_exe_path(exe_name):
    path = shutil.which(exe_name)
    if not path:
        for p in exe_paths.get(exe_name, []):
            if os.path.exists(p):
                path = p
                break
    return path


def requires_executable(exe_name):
    path = get_exe_path(exe_name)
    if not path:
        raise OSError(f"Cannot find required command: {exe_name}")

    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            return func(*args, **kwargs)
        return inner
    return wrapper


@requires_executable("iw")
def parse_devlist() -> List[InterfaceConfig]:
    interfaces = []
    proc = subprocess.run([get_exe_path("iw"), "dev"],
                           capture_output=True,
                           check=True,
                           encoding="utf-8")
    data = proc.stdout.split("\n")

    config = None
    fields = InterfaceConfig.__dataclass_fields__.keys()
    for line in data:
        line = line.strip()
        if line.startswith("Interface"):
            name = line.replace("Interface", "").strip()
            if config is not None:
                interfaces.append(config)

            config = InterfaceConfig(name=name)
            continue

        match = re.match("^(?P<key>[a-zA-Z]+)\s(?P<value>[a-zA-Z0-9 :-_]+)$", line)
        if match and match.group("key") in fields:
            setattr(config, match["key"], match["value"])

    if config:
        interfaces.append(config)

    return interfaces


def get_iface(name: str) -> Union[InterfaceConfig,None]:
    for iface in parse_devlist():
        if iface.name == name:
            return iface

    return None

class NoSuchInterface(Exception):
    pass

@requires_executable("ip")
@requires_executable("iw")
def wifi_set_monitor_mode(iface_name: str):
    """
        Set the specified interface into monitor mode.

        Args:
            iface_name: The name of the interface to configure.

        Returns: None

        Exceptions:
        If there is an error detecting or configuring the wifi card, this
        function will raise one of the following exceptions:

        NoSucInterface
            Raised if the provided interface name does not exist

        subprocess.CalledProcessError
            Raised if there was an error executing the commands to configure the
            interface

        RuntimeError
            Raised if there is an issue detecting or configuring interface after
            the system commands have executed successfully.
    """
    iface = get_iface(iface_name)
    if not iface:
        raise NoSuchInterface(iface)

    ip_cmd = get_exe_path("ip")
    iw_cmd = get_exe_path("iw")
    if iface.type != "monitor":
        subprocess.run([ip_cmd, "link", "set", iface.name, "down"], check=True)
        subprocess.run([iw_cmd, iface.name, "set", "monitor", "control"], check=True)
        subprocess.run([ip_cmd, "link", "set", iface.name, "up"])

        iface = get_iface(iface_name)
        if not iface:
            raise RuntimeError("Interface not available after re-configuring")

        if iface.type != "monitor":
            raise RuntimeError(f"Failed to set iterface into monitoring mode: {iface_name}")


@requires_executable("iw")
def wifi_set_channel(iface: str, channel: int):
    subprocess.run(["iw", "dev", iface, "set", "channel", str(channel)], check=True)