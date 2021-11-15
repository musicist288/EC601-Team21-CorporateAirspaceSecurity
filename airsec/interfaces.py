"""
    This module defines dataclasses representing the different objects
    that are serialized and deserialized from different parts of the
    system to avoid having to pass around ambiguously defined dictionaries
    or tuples.

    All interfaces should be defined in this file.
"""
from dataclasses import dataclass
from datetime import datetime
from json import JSONEncoder

@dataclass
class BeaconPacket:
    time: datetime
    bssid: str
    ssid: str
    rssi: int
    channel: int
    payload: bytes

@dataclass
class BeaconPacketAPI:
    """
        Same structure as a BeaconPacket without the payload to
        make API interface less full.
    """

    time: datetime
    bssid: str
    ssid: str
    rssi: int
    channel: int

    @classmethod
    def from_beacon_packet(cls, bp: BeaconPacket):
        return cls(time=bp.time,
                   bssid=bp.bssid,
                   ssid=bp.ssid,
                   rssi=bp.rssi,
                   channel=bp.channel)

    @classmethod
    def from_json_dict(cls, obj):
        return cls(
            time=datetime.fromisoformat(obj['time']),
            bssid=obj['bssid'],
            ssid=obj['ssid'],
            rssi=obj['rssi'],
            channel=obj['channel'],
        )

    def to_dict(self):
        d = self.__dict__
        d['time'] = d['time'].isoformat()
        return d

@dataclass
class AllowedBeacon:
    bssid: str

    @classmethod
    def from_json_dict(cls, obj):
        return cls(**obj)

class BeaconPacketEncoder(JSONEncoder):

    def default(self, obj):
        if isinstance(obj, (BeaconPacket, BeaconPacketAPI)):
            data = obj.__dict__
            return data
        elif isinstance(obj, datetime):
            return obj.isoformat()

        return super().default(obj)
