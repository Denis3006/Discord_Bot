from datetime import datetime
from urllib.parse import urlparse

import psycopg2
import psycopg2.extras
import src.Constants as Constants


def connect_to_psql():
    connection_data = urlparse(Constants.DATABASE_URL)
    connection = psycopg2.connect(
        dbname=connection_data.path[1:], user=connection_data.username,
        password=connection_data.password, host=connection_data.hostname)
    connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    return connection


def db_add_alcoholic_if_missing(user):
    cur = Constants.DB_CONNECTION.cursor()
    sql = "INSERT INTO alcoholics (id, name, alco_percent, hangover, timeout_untill, last_drink_time)" +\
          " VALUES({}, '{}', 0, false, '{}', '{}') ON CONFLICT DO NOTHING"
    cur.execute(sql.format(user.id, user.name, datetime.now(), datetime.now()))
    cur.close()
    Constants.DB_CONNECTION.commit()


def get_alcogolic_data(id: int, fields_to_get: list = None) -> psycopg2.extras.DictRow:
    cur = Constants.DB_CONNECTION.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if fields_to_get:
        cur.execute(f"SELECT {', '.join(fields_to_get)} FROM alcoholics WHERE id = {id};")
        return cur.fetchone()
    else:
        cur.execute(f"SELECT * FROM alcoholics WHERE id = {id};")
        return cur.fetchone()


def upload_alcoholic_data(id: int, data: dict):
    cur = Constants.DB_CONNECTION.cursor()
    cur.execute(f"UPDATE alcoholics SET ({', '.join(list(data.keys()))}) = " +\
                f"({', '.join([str(x) for x in list(data.values())])}) WHERE id = {id};")
    cur.close()
    Constants.DB_CONNECTION.commit()
