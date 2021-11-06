import unittest
import json
from datetime import datetime
from airsec import interfaces

class TestInterfaces(unittest.TestCase):

    def test_dataclass_encoder(self):
        bp = interfaces.BeaconPacketAPI(
            time=datetime.now(),
            bssid="11",
            ssid="Test",
            rssi=-30,
            channel=6
        )

        data = json.dumps(bp, cls=interfaces.BeaconPacketEncoder)
        parsed = json.loads(data)
        self.assertEqual(parsed['time'], bp.time.isoformat())
        self.assertEqual(parsed['bssid'], bp.bssid)
        self.assertEqual(parsed['ssid'], bp.ssid)
        self.assertEqual(parsed['rssi'], bp.rssi)
        self.assertEqual(parsed['channel'], bp.channel)
        self.assertTrue("payload" not in parsed)


    def test_datclass_decoder(self):
        bp = interfaces.BeaconPacketAPI(
            time=datetime.now(),
            bssid="11",
            ssid="Test",
            rssi=-30,
            channel=6
        )

        data = json.dumps(bp, cls=interfaces.BeaconPacketEncoder)
        parsed: interfaces.BeaconPacketAPI = json.loads(
            data,
            object_hook=interfaces.BeaconPacketAPI.from_json_dict)

        self.assertIsInstance(parsed, interfaces.BeaconPacketAPI)
        self.assertEqual(parsed, bp)
