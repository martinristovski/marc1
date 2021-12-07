import unittest
from database_services.RDBService import RDBDataTable
from utils.validator import DataValidator
import pymysql
from utils import sql_utils
from beans.form_input import FormInput
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


class Test_FormInput(unittest.TestCase):
    def setUp(self) -> None:
        self.rdb_conn = test_rdb_conn

        self.cnx = pymysql.connect(host=test_rdb_conn['host'],
                                   user=test_rdb_conn['user'],
                                   password=test_rdb_conn['password'],
                                   charset=charset,
                                   cursorclass=test_rdb_conn["cursorclass"])

        sql_utils.execute_sql_file_scripts(self.cnx, "schema.sql")

    def test_process_from_creation(self):
        body = {
            "inputs": [{
                "field_name": "First Name",
                "field_type": "str",
                "expected_values": ""
            }, {
                "field_name": "Last Name",
                "field_type": "str",
                "expected_values": ""
            }, {
                "field_name": "Age",
                "field_type": "int"
            }, {
                "field_name": "Date of Birth",
                "field_type": "str",
                "expected_values": ""
            }, {
                "field_name": "Gender",
                "field_type": "str",
                "expected_values": "M,F"
            }
            ],
            "endpoints": ["http://www.xyz.com/", "http://www.abc.edu/"]
        }

        form_creation_request = FormInput(body)

        form_id = "test_form"
        uuid = "001c38a3-7e7e-4da1-8ad9-b67f03182baa"

        form_creation_request.process_form_creation(
            form_id, uuid, rdb_conn=test_rdb_conn)
        reason = form_creation_request.validate_form_values()
        self.assertEqual(reason, "")

        check_for_form_query = f"SELECT * FROM form_info WHERE " \
                               f"uuid='{uuid}' AND form_id='{form_id}';"
        res = sql_utils.run_query(check_for_form_query, self.cnx, fetch=True)
        self.assertEqual(len(res), 1)

    def test_validate_form_values(self):
        data_val_obj = DataValidator()
        form_objects = {
            'input_empty': {
                'form_object': {
                    'endpoints': ["ciao"]
                },
                'reason': "Key input is missing"
            },
            'endpoints_empty': {
                'form_object': {
                    'inputs': ["ciao"]
                },
                'reason': "Key endpoints is missing"
            },
            'none_input_field_name': {
                'form_object': {
                    'inputs': [
                        {
                            "field_name": "First Name",
                            "field_type": "str",
                            "expected_values": ""
                        },
                        {
                            "field_name": None,
                            "field_type": "str",
                            "expected_values": ""
                        },
                    ],
                    'endpoints': ["ciao"]
                },
                'reason': "One of the input field name is empty"
            },
            'empty_input_field_name': {
                'form_object': {
                    'inputs': [
                        {
                            "field_name": "First Name",
                            "field_type": "str",
                            "expected_values": ""
                        },
                        {
                            "field_name": "",
                            "field_type": "str",
                            "expected_values": ""
                        },
                    ],
                    'endpoints': ["ciao"]
                },
                'reason': "One of the input field name is empty"
            },
            'invalid_field_type': {
                'form_object': {
                    'inputs': [
                        {
                            "field_name": "First Name",
                            "field_type": "str",
                            "expected_values": ""
                        },
                        {
                            "field_name": "Last Name",
                            "field_type": "strnz",
                            "expected_values": ""
                        },
                    ],
                    'endpoints': ["ciao"]
                },
                'reason': f"Invalid field_type = strnz received. "
                          f"Valid types={data_val_obj.get_all_valid_types()}"
            },
            'cool_runnings': {
                'form_object': {
                    'inputs':
                        [
                            {"field_name": "First Name",
                             "field_type": "str",
                             "expected_values": ""},
                            {"field_name": "Last Name",
                             "field_type": "str",
                             "expected_values": ""},
                            {"field_name": "Age",
                             "field_type": "int"},
                            {"field_name": "Date of Birth",
                             "field_type": "str",
                             "expected_values": ""},
                            {"field_name": "Gender",
                             "field_type": "str",
                             "expected_values": "M,F"}],
                    'endpoints': ["cesare.com"]
                },
                'reason': ""
            },
        }

        for k, v in form_objects.items():
            form_creation_request = FormInput(v['form_object'])
            reason = form_creation_request.validate_form_values()

            self.assertEqual(reason, v['reason'])

    def test_delete_form_record(self):
        body = {
            "inputs": [{
                "field_name": "First Name",
                "field_type": "str",
                "expected_values": ""
            }, {
                "field_name": "Last Name",
                "field_type": "str",
                "expected_values": ""
            }, {
                "field_name": "Age",
                "field_type": "int"
            }, {
                "field_name": "Date of Birth",
                "field_type": "str",
                "expected_values": ""
            }, {
                "field_name": "Gender",
                "field_type": "str",
                "expected_values": "M,F"
            }
            ],
            "endpoints": ["http://www.xyz.com/", "http://www.abc.edu/"]
        }

        form_input_obj = FormInput(body)

        form_id = "test_form"
        uuid = "001c38a3-7e7e-4da1-8ad9-b67f03182baa"

        form_input_obj.process_form_creation(
            form_id, uuid, rdb_conn=test_rdb_conn)
        database_service = RDBDataTable("form_info", test_rdb_conn)
        current_count = database_service.get_no_of_rows()
        form_input_obj.delete_form_record("test_form",
                                          rdb_conn=test_rdb_conn)
        new_count = database_service.get_no_of_rows()
        diff = current_count - new_count
        self.assertEqual(diff, 1)

    def tearDown(self) -> None:
        sql_utils.clear_db(self.cnx, os.environ.get('RDBSCHEMA', None))
