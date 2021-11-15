import sqlite3
from sqlite3 import Error
import logging
import pymysql

logger = logging.getLogger()

cursorClass = pymysql.cursors.DictCursor
charset = 'utf8mb4'
connect_info = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '',
    'cursorclass': cursorClass
}


def execute_sql_file_scripts(cnx, filename):
    file = open(filename, 'r')
    sql_schema = file.read()
    file.close()

    sql_commands = sql_schema.split(';')

    for comm in sql_commands:
        comm = comm.strip()
        if comm == '':
            continue
        res = run_query(comm, cnx)



def run_query(query, cnx, commit=True, fetch=False):
    try:
        cursor = cnx.cursor()

        result = cursor.execute(query)
        if fetch:
            result = cursor.fetchall()
        else:
            result = result

        if commit:
            cursor.close()
        cursor.close()

    except Exception as e:
        print('run_query', e)
        raise e

    return result


def clear_db(cnx, db_name):

    run_query(f"DROP DATABASE {db_name}", cnx)
    cnx.close()