from dataclasses import dataclass

@dataclass
class WifiPacket:
    timestamp: float

    src_addr: str
    recv_addr: str

    dst_addr: str
    rssi: str
