import unittest
from database_services.RDBService import RDBDataTable
import pymysql
from utils import sql_utils
from beans.form_input import FormInput
import secrets
import os

cursorClass = pymysql.cursors.DictCursor
charset = 'utf8mb4'

test_rdb_conn = {
    'host': os.environ.get('DBHOST', None),
    'user': os.environ.get('DBUSER', None),
    'password': os.environ.get('DBPASSWORD', None),
    'cursorclass': pymysql.cursors.DictCursor,
    'db': os.environ.get('RDBSCHEMA', None)
}

class Test_RDBService(unittest.TestCase):
	def setUp(self) -> None:
		self.rdb_conn = test_rdb_conn
		self.cnx = pymysql.connect(host=test_rdb_conn['host'],
                                   user=test_rdb_conn['user'],
                                   password=test_rdb_conn['password'],
                                   charset=charset,
                                   cursorclass=test_rdb_conn["cursorclass"])

		sql_utils.execute_sql_file_scripts(self.cnx, "schema.sql")
		self.table_name = "form_info"
		self.key_columns = ["form_id"]
		self.column_list = ["form_id", "uuid", "modified_at"]
		self.db_service = RDBDataTable(self.table_name, self.rdb_conn, self.key_columns)

	def test_get_column_names(self):
		received_column_list = self.db_service.get_column_names().sort()
		original_column_list = self.column_list.sort()
		are_equal = original_column_list == received_column_list
		self.assertTrue(are_equal)

	def test_get_no_of_rows(self):
		row_count = self.db_service.get_no_of_rows()
		self.assertEqual(row_count, 0)

	def test_get_key_columns(self):
		received_col_list = self.db_service.get_key_columns().sort()
		original_col_list = self.column_list.sort()
		self.assertTrue(original_col_list == received_col_list)

	def test_find_by_template_limit_offset(self):
		template = None
		result = self.db_service.find_by_template(template, limit=10, offset=10)
		self.assertIsNotNone(result)

	def test_update(self):
		row = {}
		row["form_id"] = "test_form"
		row["uuid"] = "test_uuid"
		insert_count = self.db_service.insert(row)
		self.assertEqual(insert_count, 1)
		template = {}
		template["form_id"] = "test_form"
		update_row = {}
		update_row["uuid"] = "updated_test_uuid"
		update_count = self.db_service.update(template, update_row)
		self.assertEqual(update_count, 1)

	def tearDown(self) -> None:
		sql_utils.clear_db(self.cnx, os.environ.get('RDBSCHEMA', None))