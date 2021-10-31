from datetime import datetime
import unittest

from airsec import config
from airsec import db

class DatabaseTest(unittest.TestCase):
    """Baseclass for database unit tests.

    The setUp and tearDown for all database tests will create and drop tables
    in-between each tests to get back to a clean starting point.
    """

    def setUp(self):
        super().setUp()

        conf = config.load()
        if not conf.timescaledb_test_dbname:
            self.skipTest("Skipping datatbase test. Test DB is not configured.")

        db.set_active_database(conf.timescaledb_test_dbname)
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
        db.WifiAllowList.add(bssid)
        data = db.WifiAllowList.select()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['bssid'], bssid)


    def test_add_multiple_bssids(self):
        bssids = [
            "11:22:33:44:55:66",
            "77:88:99:11:22:33"
        ]
        db.WifiAllowList.add(bssids)
        data = db.WifiAllowList.select()
        self.assertEqual(len(data), len(bssids))
        for bid, rec in zip(bssids, data):
            self.assertEqual(rec['bssid'], bid)


class WifiPacketTests(DatabaseTest):

    def test_log_wifi_packet(self):
        date = datetime.now()
        bssid = "11:22:33:44:55:66"
        rssi = -39
        db.WifiPacket.add(date, bssid, rssi)
        result = db.WifiPacket.select(filter=f"WHERE bssid = '{bssid}'")
        self.assertEqual(len(result), 1)
        result = result[0]
        self.assertEqual(result['bssid'], bssid)
        self.assertEqual(result['rssi'], rssi)
        self.assertEqual(result['time'], date)