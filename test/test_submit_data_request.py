import unittest
import pymysql
from utils import sql_utils
from database_services.RDBService import RDBDataTable
import uuid
import secrets
from test.helpers_tst import create_form_helper
import os
from beans.submit_data_request import SubmitFormDataRequest

cursorClass = pymysql.cursors.DictCursor
charset = 'utf8mb4'

test_rdb_conn = {
    'host': os.environ.get('DBHOST', None),
    'user': os.environ.get('DBUSER', None),
    'password': os.environ.get('DBPASSWORD', None),
    'cursorclass': pymysql.cursors.DictCursor,
    'db': os.environ.get('RDBSCHEMA', None)
}

mdb_connect_info = {
    "URL": os.environ.get('MONGO_URL', None),
    "PORT": 27017,
    "DB": "Test_From"

}


class Test_SubmitDataRequest(unittest.TestCase):

    def setUp(self) -> None:
        # Set up testing environment
        self.rdb_conn = test_rdb_conn

        self.cnx = pymysql.connect(host=test_rdb_conn['host'],
                                   user=test_rdb_conn['user'],
                                   password=test_rdb_conn['password'],
                                   charset=charset,
                                   cursorclass=test_rdb_conn["cursorclass"])

        sql_utils.execute_sql_file_scripts(self.cnx, "schema.sql")
        self.mdb_con_info = mdb_connect_info

        # Add uuid and api_key to developer_info
        dev_uuid = uuid.uuid4()
        api_key = secrets.token_urlsafe(32)
        row = {'uuid': dev_uuid.__str__(), 'api_key': api_key}
        database_service = RDBDataTable(
            "developer_info",
            connect_info=test_rdb_conn,
            key_columns=["uuid"])
        database_service.insert(row)

        self.uuid = dev_uuid.__str__()
        self.api_key = api_key

        form_input_endpoints = {
            'inputs': [
                {
                    "field_name": "First Name",
                    "field_type": "str",
                    "expected_values": ""
                }
            ],
            'endpoints': ["marc1.com"]
        }
        form_id_ep, reason_ep = create_form_helper(
            form_input_endpoints, self.uuid, self.rdb_conn)

        self.form_id = form_id_ep

    def test_validate_form_request(self):
        form_response = {
            "form_id": self.form_id,
            "submission_data": [{
                "field_name": "First Name",
                "field_value": "Rishav"
            }]
        }
        submit_form_obj = SubmitFormDataRequest(form_response)
        ret_val = submit_form_obj.validate_form_request(self.rdb_conn)
        self.assertTrue(ret_val)

    def test_validate_form_request_invalid_form_id(self):
        form_response = {
            "form_id": "apple",
            "submission_data": [{
                "field_name": "First Name",
                "field_value": "Rishav"
            }]
        }
        submit_form_obj = SubmitFormDataRequest(form_response)
        ret_val = submit_form_obj.validate_form_request(self.rdb_conn)
        self.assertFalse(ret_val)

    def test_parse_form_data(self):
        form_response = {
            "form_id": self.form_id,
            "submission_data": [{
                "field_name": "First Name",
                "field_value": "Rishav"
            }]
        }

        expected_dict = {}
        expected_dict['First Name'] = "Rishav"
        submit_form_obj = SubmitFormDataRequest(form_response)
        submission_dict = submit_form_obj.parse_form_data()
        self.assertDictEqual(submission_dict, expected_dict)

    def test_validate_form_data(self):
        form_response = {
            "form_id": self.form_id,
            "submission_data": [{
                "field_name": "First Name",
                "field_value": "Rishav"
            }]
        }

        expected_dict = {}
        expected_dict['First Name'] = "Rishav"
        submit_form_obj = SubmitFormDataRequest(form_response)
        submission_dict = submit_form_obj.parse_form_data()
        reason = submit_form_obj.validate_form_data(submission_dict,
                                                    self.rdb_conn)
        self.assertEqual(reason, "")

    def test_validate_form_data_invalid_field_value(self):
        form_response = {
            "form_id": self.form_id,
            "submission_data": [{
                "field_name": "First Name",
                "field_value": 24
            }]
        }

        expected_dict = {}
        expected_dict['First Name'] = "Rishav"
        submit_form_obj = SubmitFormDataRequest(form_response)
        submission_dict = submit_form_obj.parse_form_data()
        reason = submit_form_obj.validate_form_data(submission_dict,
                                                    self.rdb_conn)
        self.assertNotEqual(reason, "")

    def test_validate_form_data_invalid_field_name(self):
        form_response = {
            "form_id": self.form_id,
            "submission_data": [{
                "field_name": "FirstSSS",
                "field_value": "Rishav"
            }]
        }

        expected_dict = {}
        expected_dict['First Name'] = "Rishav"
        submit_form_obj = SubmitFormDataRequest(form_response)
        submission_dict = submit_form_obj.parse_form_data()
        reason = submit_form_obj.validate_form_data(submission_dict,
                                                    self.rdb_conn)
        self.assertNotEqual(reason, "")

    def test_save_data(self):
        form_response = {
            "form_id": self.form_id,
            "submission_data": [{
                "field_name": "First Name",
                "field_value": "Rishav"
            }]
        }

        expected_dict = {}
        expected_dict['First Name'] = "Rishav"
        submit_form_obj = SubmitFormDataRequest(form_response)
        submission_dict = submit_form_obj.parse_form_data()
        submit_form_obj.validate_form_data(submission_dict, self.rdb_conn)
        response_id = submit_form_obj.save_data(self.form_id, submission_dict,
                                                mongodb_conn=self.mdb_con_info)
        self.assertNotEqual(response_id, "")

    def tearDown(self) -> None:
        sql_utils.clear_db(self.cnx, os.environ.get('RDBSCHEMA', None))
