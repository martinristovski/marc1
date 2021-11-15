import unittest
from utils.validator import DataValidator
import pymysql
from utils import sql_utils
from database_services.RDBService import RDBDataTable
import uuid
import secrets

cursorClass = pymysql.cursors.DictCursor
charset = 'utf8mb4'

test_rdb_conn = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '',
    'db': 'marc1_db',
    'cursorclass': pymysql.cursors.DictCursor
}

class Test_FormInput(unittest.TestCase):
    def setUp(self) -> None:
        self.rdb_conn = test_rdb_conn

        self.cnx = pymysql.connect(host=test_rdb_conn['host'],
                                   user=test_rdb_conn['user'],
                                   password=test_rdb_conn['password'],
                                   charset=charset,
                                   cursorclass=test_rdb_conn["cursorclass"])

        sql_utils.execute_sql_file_scripts(self.cnx, "schema.sql")

    def test_validate_uuid_api_key(self):
        # Add row to RDB Table
        dev_uuid = uuid.uuid4()
        print(dev_uuid.__str__(), 'aaaa')
        api_key = secrets.token_urlsafe(32)
        row = {}
        row['uuid'] = dev_uuid.__str__()
        row['api_key'] = api_key
        database_service = RDBDataTable("developer_info", connect_info=test_rdb_conn, key_columns=["uuid"])
        database_service.insert(row)

        res = DataValidator.validate_uuid_api_key(dev_uuid.__str__(), api_key, rdb_conn=self.rdb_conn)
        self.assertEqual(res, "")

        # Check that it fails correctly
        res = DataValidator.validate_uuid_api_key("AAA", "BBB", rdb_conn=self.rdb_conn)
        self.assertNotEqual(res, "")



    def tearDown(self) -> None:
        sql_utils.clear_db(self.cnx, 'marc1_db')
