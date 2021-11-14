import unittest
import json
import pymysql
import copy         # Copy data structures.
import pymysql.cursors
from database_services.RDBService import RDBDataTable

cursorClass = pymysql.cursors.DictCursor
charset = 'utf8mb4'

connect_info = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '',
    'cursorclass': pymysql.cursors.DictCursor
}

class Test_RDBService(unittest.TestCase):
    def setUp(self):
        self.cnx = pymysql.connect(host=connect_info['host'],
                              user=connect_info['user'],
                              password=connect_info['password'],
                              charset=charset,
                              cursorclass=connect_info["cursorclass"])

    def test_create_sql_from_schema(self):
        file = open('schema.sql', 'r')
        sql_schema = file.read()
        file.close()

        sql_commands = sql_schema.split(';')

        for comm in sql_commands:
            print(comm)

