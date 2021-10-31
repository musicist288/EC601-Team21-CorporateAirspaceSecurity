from contextlib import contextmanager
from datetime import datetime, timezone
import json
from typing import Union, Tuple

import psycopg2
from dateutil import tz

from . import config

class DBConnection:
    """Helper class to manage a single connection per process."""

    def __init__(self):
        # Note that everything here is not set in init so the top
        # level module can create a single connection class without
        # needing to load outside resources at startup.
        self.connection = None
        self.username = None
        self.password = None
        self.host = None
        self.port = None
        self.active_database = None

    def load_config(self, conf: config.AirsecConfig, database=None):
        self.username = conf.timescaledb_username
        self.password = conf.timescaledb_password
        self.host = conf.timescaledb_hostname
        self.port = conf.timescaledb_port
        self.active_database = database

    @property
    def connection_string(self):
        return "postgres://{username}:{password}@{host}:{port}/{active_db}".format(
            username=self.username,
            password=self.password,
            host=self.host,
            port=self.port,
            active_db=self.active_database
        )

    def connect(self):
        if self.connection is None:
            self.connection = psycopg2.connect(self.connection_string)

    def close(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def set_active_database(self, db_name: str):
        was_connected = self.connection is not None
        self.close()
        self.active_database = db_name
        if was_connected:
            self.connect()

    @contextmanager
    def cursor(self):
        if self.connection is None:
            raise RuntimeError("Not connected to a database.")

        cursor = self.connection.cursor()
        yield cursor
        cursor.close()


DATABASE = DBConnection()
@contextmanager
def get_cursor():
    with DATABASE.cursor() as cursor:
        yield cursor

class Table:

    is_hypertable = False
    hypertable_field_name = 'time'

    @classmethod
    def create(cls):
        required_fields = ['name', 'fields']
        for field in required_fields:
            if not hasattr(cls, field) or not getattr(cls, field):
                raise ValueError("Cannot create table for %s. '%s' not defined." % (cls.__class__.__name__, field))

        with get_cursor() as cursor:
            field_strs = [" ".join(f) for f in cls.fields]

            sql = """
            CREATE TABLE IF NOT EXISTS {table_name} (
                {fields}
            );
            """.format(table_name=cls.name,
                       fields=",".join(field_strs)).strip().replace("\n", "")

            cursor.execute(sql)

            if cls.is_hypertable:
                sql = "SELECT create_hypertable('{table_name}', '{field}', if_not_exists => TRUE);".format(
                    table_name=cls.name,
                    field=cls.hypertable_field_name)
                cursor.execute(sql)

    @classmethod
    def column_names(cls):
        return [f[0] for f in cls.fields]


#####################
### Table Definitions
#####################

TABLES = []

def register_table(cls):
    if not issubclass(cls, Table):
        raise TypeError("Registered tables must subclass Table")

    TABLES.append(cls)
    return cls


@register_table
class WifiPacket(Table):

    name = "wifi_packet"
    fields = (
        ("time", "TIMESTAMP WITHOUT TIME ZONE", "NOT NULL"),
        ("bssid", "MACADDR", "NOT NULL"),
        ("rssi", "INTEGER", "NOT NULL")
    )
    is_hypertable = True

    date_format = "%Y-%m-%dT%H:%M:%S.%f"

    @classmethod
    def add(cls, dt: datetime, bssid: str, rssi: int):
        timestamp = dt.astimezone(timezone.utc).strftime(cls.date_format)
        values = f"('{timestamp}', '{bssid}', '{rssi}')"
        sql = f"INSERT INTO {cls.name} VALUES {values};"
        with get_cursor() as cursor:
            cursor.execute(sql)


    @classmethod
    def select(cls, filter=""):
        data = []
        column_names = cls.column_names()
        sql = f"SELECT * FROM {cls.name} {filter};"
        with get_cursor() as cursor:
            cursor.execute(sql)
            results = cursor.fetchall()
            for r in results:
                record = dict(zip(column_names, r))
                record['time'] = (record['time'].replace(tzinfo=tz.tzutc())
                                                .astimezone(tz.tzlocal())
                                                .replace(tzinfo=None))
                data.append(record)

        return data


@register_table
class WifiAllowList(Table):
    name = "wifi_allow_list"
    fields = (
        ("bssid", "MACADDR", "NOT NULL"),
    )

    @classmethod
    def add(cls, bssid: Union[str, list, Tuple]) -> None:
        if isinstance(bssid, str):
            bssid = (bssid,)

        sql = """
        INSERT INTO {name} (bssid)
        SELECT
            bssid
        FROM json_populate_recordset(null::{name}, %s);""".format(name=cls.name)

        values = [{"bssid": b} for b in bssid]
        with get_cursor() as cursor:
            cursor.execute(sql, (json.dumps(values), ))


    @classmethod
    def select(cls, filter=""):
        data = []
        column_names = [f[0] for f in cls.fields]
        columns = ",".join(column_names)

        sql = f"""
        SELECT {columns} FROM {cls.name} {filter}
        """

        with get_cursor() as cur:
            cur.execute(sql)
            results = cur.fetchall()
            for r in results:
                data.append(dict(zip(column_names, r)))

        return data

# Environment Macros for grouping config variables
ENVIRONMENTS = {
    "production": {
        "database_key": "timescaledb_dbname"
    },
    "test": {
        "database_key": "timescaledb_test_dbname"
    }
}


##############################
# Public API Helper functions
##############################

def init(env="production"):
    conf = config.load()
    DATABASE.load_config(conf)

    if env not in ENVIRONMENTS:
        raise ValueError("Unknown environment: %s" % env)

    dbname_key = ENVIRONMENTS[env]["database_key"]
    db_name = getattr(conf, dbname_key)
    if not db_name:
        raise ValueError("%s database name not defined in config: %s" % (env, dbname_key))

    DATABASE.set_active_database(db_name)
    DATABASE.connect()


def setup_database() -> None:
    with get_cursor() as cursor:
        cursor.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;");

    for table in TABLES:
        table.create()


if __name__ == "__main__":
    init()
    setup_database()
