import unittest
from utils.validator import DataValidator
import pymysql
from utils import sql_utils
from database_services.RDBService import RDBDataTable

cursorClass = pymysql.cursors.DictCursor
charset = 'utf8mb4'

connect_info = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '',
    'cursorclass': pymysql.cursors.DictCursor
}

class Test_DataValidator(unittest.TestCase):
    def setUp(self) -> None:
        self.context = {
            'host': '127.0.0.1',
            'user': 'root',
            'password': '',
            'db': 'marc1_db',
            'cursorclass': pymysql.cursors.DictCursor
        }

        self.cnx = pymysql.connect(host=connect_info['host'],
                                   user=connect_info['user'],
                                   password=connect_info['password'],
                                   charset=charset,
                                   cursorclass=connect_info["cursorclass"])

        sql_utils.execute_sql_file_scripts(self.cnx, "schema.sql")

    def test_generate_uuid_api(self):
        data_validator = DataValidator(self.context)
        uuid, api_key = data_validator.generate_uuid_api_key()

        # Check that api_key and dev_uuid have been added to table
        rdb_data = RDBDataTable('developers', self.context)
        row = rdb_data.find_by_template(None)[0]

        self.assertEqual(row['uuid'], uuid.__str__())
        self.assertEqual(row['api_key'], api_key)

    def test_validate_uuid_api_key(self):
        data_validator = DataValidator(self.context)
        uuid, api_key = data_validator.generate_uuid_api_key()
        uuid2, api_key2 = data_validator.generate_uuid_api_key()

        res = data_validator.validate_uuid_api_key(uuid.__str__(), api_key)

        self.assertEqual(res, "")

        # Check that it fails correctly
        res = data_validator.validate_uuid_api_key("AAA", "BBB")
        self.assertNotEqual(res, "")



    def tearDown(self) -> None:
        sql_utils.clear_db(self.cnx, 'marc1_db')
