from dataclasses import dataclass
from datetime import datetime

@dataclass
class BeaconPacket:
    time: datetime
    bssid: str
    ssid: str
    rssi: int
    channel: int
    payload: bytes