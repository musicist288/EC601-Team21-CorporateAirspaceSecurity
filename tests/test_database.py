from datetime import datetime
import unittest

from airsec import (
    db,
    interfaces
)

class DatabaseTest(unittest.TestCase):
    """Baseclass for database unit tests.

    The setUp and tearDown for all database tests will create and drop tables
    in-between each tests to get back to a clean starting point.
    """

    def setUp(self):
        super().setUp()

        try:
            db.init("test")
        except ValueError as err:
            self.skipTest("Skipping tests due to an error: %s" % err)

        db.setup_database()


    def tearDown(self) -> None:
        with db.get_cursor() as cursor:
            for table in db.TABLES:
                cursor.execute(f"DROP TABLE {table.name}")

        return super().tearDown()


class TestDatabaseSetup(DatabaseTest):

    def test_tables_created(self):
        with db.get_cursor() as cursor:
            for table in db.TABLES:
                sql = f"""SELECT table_name
                          FROM information_schema.columns
                          WHERE table_name = '{table.name}';""".strip()
                cursor.execute(sql)
                records = cursor.fetchall()
                self.assertEqual(len(records), len(table.fields))
                self.assertEqual(records[0][0], table.name)


class WifiAllowListTest(DatabaseTest):

    def test_add_bssid(self):
        bssid = "11:22:33:44:55:66"
        db.AllowedBeacons.add(bssid)
        data = db.AllowedBeacons.select()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0].bssid, bssid)


    def test_add_multiple_bssids(self):
        bssids = [
            "11:22:33:44:55:66",
            "77:88:99:11:22:33"
        ]
        db.AllowedBeacons.add(bssids)
        data = db.AllowedBeacons.select()
        self.assertEqual(len(data), len(bssids))
        for bid, rec in zip(bssids, data):
            self.assertEqual(rec.bssid, bid)


class WifiPacketTests(DatabaseTest):

    def test_log_wifi_packet(self):
        date = datetime.now()
        bssid = "11:22:33:44:55:66"
        ssid = "InternetAP"
        channel = 6
        rssi = -39
        payload = b"\x01" * 30
        db.BeaconPacket.add(date, bssid, ssid, channel, rssi, payload)
        result = db.BeaconPacket.select(filter=f"WHERE bssid = '{bssid}'")
        self.assertEqual(len(result), 1)
        result = result[0]
        self.assertEqual(result.bssid, bssid)
        self.assertEqual(result.rssi, rssi)
        self.assertEqual(result.time, date)
        self.assertEqual(result.payload, payload)
        self.assertEqual(result.ssid, ssid)


    def test_conditional_insert_unauthorized(self):
        date = datetime.now()
        bssid = "11:22:33:44:55:66"
        ssid = "InternetAP"
        channel = 6
        rssi = -39
        payload = b"\x01" * 30
        packet = interfaces.BeaconPacket(
            time=date,
            bssid=bssid,
            ssid=ssid,
            channel=channel,
            rssi=rssi,
            payload=payload)

        db.add_packet_if_unauthorized(packet)
        data = db.BeaconPacket.select()
        self.assertEqual(len(data), 1)

    def test_conditional_insert_authorized(self):
        date = datetime.now()
        bssid = "11:22:33:44:55:66"
        ssid = "InternetAP"
        channel = 6
        rssi = -39
        payload = b"\x01" * 30
        packet = interfaces.BeaconPacket(
            time=date,
            bssid=bssid,
            ssid=ssid,
            channel=channel,
            rssi=rssi,
            payload=payload)

        db.AllowedBeacons.add(bssid)
        db.add_packet_if_unauthorized(packet)
        data = db.BeaconPacket.select()
        self.assertEqual(len(data), 0)
