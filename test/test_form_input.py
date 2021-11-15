import unittest
from utils.validator import DataValidator
import pymysql
from utils import sql_utils
from database_services.RDBService import RDBDataTable
from beans.form_input import FormInput
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

    def test_validate_form_values(self):
        form_objects = {
            'input_empty': {
               'form_object': {
                   'endpoints': ["ciao"]
               },
               'reason': f"Key input is missing"
            },
            'endpoints_empty': {
               'form_object': {
                   'inputs': ["ciao"]
               },
               'reason': f"Key endpoints is missing"
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
                'reason': f"Invalid field_type = strnz received. Valid types={DataValidator.get_all_valid_types()}"
            },
            'cool_runnings': {
                'form_object': {
                    'inputs': [
                        {
                        "field_name": "First Name",
                        "field_type": "str",
                        "expected_values": ""
                         },
                        {
                        "field_name": "Last Name",
                        "field_type": "str",
                        "expected_values": ""
                        },
                        {
                        "field_name": "Age",
                        "field_type": "int"
                        },
                        {
                        "field_name": "Date of Birth",
                        "field_type": "str",
                        "expected_values": ""
                        },
                        {
                        "field_name": "Gender",
                        "field_type": "str",
                        "expected_values": "M,F"
                         }],
                    'endpoints': ["cesare.com"]
                },
                'reason': ""
            },
       }

        for k, v in form_objects.items():
            print(k)
            form_creation_request = FormInput(v['form_object'])
            reason = form_creation_request.validate_form_values()

            self.assertEqual(reason, v['reason'])

    def tearDown(self) -> None:
        sql_utils.clear_db(self.cnx, 'marc1_db')
