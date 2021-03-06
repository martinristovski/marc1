import unittest
import os
import pymysql
import pymysql.cursors
import utils.sql_utils as sql_utils
cursorClass = pymysql.cursors.DictCursor
charset = 'utf8mb4'

connect_info = {
    'host': os.environ.get('DBHOST', None),
    'user': os.environ.get('DBUSER', None),
    'password': os.environ.get('DBPASSWORD', None),
    'cursorclass': pymysql.cursors.DictCursor
}


class Test_sql_utils(unittest.TestCase):
    def setUp(self):
        self.cnx = pymysql.connect(host=connect_info['host'],
                                   user=connect_info['user'],
                                   password=connect_info['password'],
                                   charset=charset,
                                   cursorclass=connect_info["cursorclass"])

    def test_create_sql_from_schema(self):
        db_name = os.environ.get('RDBSCHEMA', None)

        sql_utils.execute_sql_file_scripts(self.cnx, 'schema.sql')

        db_check = f"SHOW DATABASES LIKE '%{db_name}%';"

        # Check db has been successfully created
        res = sql_utils.run_query(db_check, self.cnx, fetch=True)
        self.assertEqual(len(res), 1)

        # Check tables have been created successfully
        self.cnx.select_db(db_name)

        print('')
        show_tables = f"SHOW TABLES IN {db_name}"
        res = sql_utils.run_query(show_tables, self.cnx, fetch=True)

        print('db', res)

    def tearDown(self) -> None:
        sql_utils.clear_db(self.cnx, os.environ.get('RDBSCHEMA', None))
