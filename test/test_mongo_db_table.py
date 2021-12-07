import unittest
from database_services.MongoDBTable import MongoDBTable
import pymysql
import os

cursorClass = pymysql.cursors.DictCursor
charset = 'utf8mb4'

db_connect_info = {
    "URL": os.environ.get('MONGO_URL', None),
    "PORT": 27017,
    "DB": "Test_From"

}

mdb_conn = {
    'conn_url': db_connect_info,
    'table_name': "form_test",
    'primary_key': ["user_id"]
}


class Test_MongoDBTable(unittest.TestCase):
    def setUp(self) -> None:
        self.mdb_client = MongoDBTable(mdb_conn['table_name'],
                                       mdb_conn['conn_url'],
                                       key_columns=mdb_conn['primary_key'])

    def test_insert(self):
        new_row = {}
        new_row['first_name'] = 'Rishav'
        new_row['last_name'] = 'Kumar'
        new_row['age'] = 24
        new_row['phone'] = '5512561111'
        new_row['user_id'] = "1111"
        result = self.mdb_client.insert(new_row)
        self.assertIsNotNone(result)

    def test_template_find(self):
        template = {}
        template['first_name'] = 'Rishav'
        res = self.mdb_client.find_by_template(template)
        print(res)
        self.assertNotEqual(len(res), 0)

    def test_z1_delete_by_template(self):
        template = {}
        template['last_name'] = 'Kumar'
        delete_count = self.mdb_client.delete_by_template(template)
        self.assertEqual(delete_count, 1)

    def tearDown(self) -> None:
        pass
