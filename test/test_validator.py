import unittest
from utils.validator import DataValidator
import pymysql
from utils import sql_utils
from database_services.RDBService import RDBDataTable
import uuid
import secrets
from test.helpers_tst import Request, create_form_helper
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

class Test_DataValidator(unittest.TestCase):

    def setUp(self) -> None:
        # Set up testing environment
        self.rdb_conn = test_rdb_conn

        self.cnx = pymysql.connect(host=test_rdb_conn['host'],
                                   user=test_rdb_conn['user'],
                                   password=test_rdb_conn['password'],
                                   charset=charset,
                                   cursorclass=test_rdb_conn["cursorclass"])

        sql_utils.execute_sql_file_scripts(self.cnx, "schema.sql")
        self.mdb_connect_info = mdb_connect_info
        self.data_validator_obj = DataValidator()
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

    def test_get_all_users_form(self):
        form_list_resp = self.data_validator_obj.get_all_users_form(self.uuid, self.rdb_conn)
        self.assertEqual(len(form_list_resp), 0)

    def test_get_value_type(self):
        """
            Checks that get_value_type correctly returns different types
        """
        test_types = {
            'int': int,
            'float': float,
            'bool': bool,
            'str': str,
            'ciao': None
        }

        for k, v in test_types.items():
            val = self.data_validator_obj.get_value_type(k)
            self.assertEqual(v, val)

    def test_validate_uuid_api_key(self):
        """
            Test by generating uuid and api_key with logic
            from app.py developer/register endpoint
            Call validate_uuid_api_key with an existing uuid,
            api_key tuple and with one that doesn't existd
        """

        # Test that dev_uuid and api_key have been added to developer_info
        res = self.data_validator_obj.validate_uuid_api_key(
            self.uuid.__str__(),
            self.api_key,
            rdb_conn=self.rdb_conn)
        self.assertEqual(res, "")


    # TODO
    def test_validate_uuid_api_key_invalid_api_key(self):
        res = self.data_validator_obj.validate_uuid_api_key(
            self.uuid.__str__(), "BBB", rdb_conn=self.rdb_conn)
        self.assertNotEqual(res, "")        
        

    def test_validate_uuid_api_key_invalid_uuid(self):
        # Check that it fails correctly
        res = self.data_validator_obj.validate_uuid_api_key(
            "AAA", self.api_key, rdb_conn=self.rdb_conn)
        self.assertNotEqual(res, "")


    # Recheck
    def test_validate_uuid_form_id(self):
        """
            Create dummy form and check that form_id
            is added to table and that uuid is
            correctly associated
        """
        form_input = {
            'inputs': [
                {
                    "field_name": "First Name",
                    "field_type": "str",
                    "expected_values": ""
                }
            ],
            'endpoints': ["marc1.com"]
        }

        form_id, reason = create_form_helper(
            form_input, self.uuid, self.rdb_conn)
        self.assertEqual(reason, "")

        # Check that form_id has been added correctly
        response = self.data_validator_obj.validate_uuid_form_id(
            self.uuid, form_id, rdb_conn=self.rdb_conn)
        self.assertEqual(response, "")

        # Test for unknown form_id
        wrong_form_id = "cdmcdmcdmcdm"
        response = self.data_validator_obj.validate_uuid_form_id(
            self.uuid, wrong_form_id, rdb_conn=self.rdb_conn)
        self.assertNotEqual(response, "")

        # Test for unknown uuid
        wrong_uuid = "uuip"
        response = self.data_validator_obj.validate_uuid_form_id(
            wrong_uuid, form_id, rdb_conn=self.rdb_conn)
        self.assertNotEqual(response, "")

    def test_validate_request_endpoint(self):
        # Create form with endpoints
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
        self.assertEqual(reason_ep, "")

        # Check referrer = None returns False
        request = Request({})
        resp = self.data_validator_obj.validate_request_endpoint(
            request, form_id_ep, rdb_conn=self.rdb_conn)
        self.assertEqual(resp, False)

        # Check referrer not in endpoints returns false
        request = Request({'Referrer': "wat up"})
        resp = self.data_validator_obj.validate_request_endpoint(
            request, form_id_ep, rdb_conn=self.rdb_conn)
        self.assertEqual(resp, False)

        # Check correct referrer is found
        request = Request({'Referrer': "marc1.com"})
        resp = self.data_validator_obj.validate_request_endpoint(
            request, form_id_ep, rdb_conn=self.rdb_conn)
        self.assertEqual(resp, True)

    def test_fetch_form_response(self):

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

        form_response = {
            "form_id": form_id_ep,
            "submission_data": [{
                "field_name": "First Name",
		        "field_value": "Rishav"
            }]
        }

        expected_dict = {}
        expected_dict['First Name'] = "Rishav"
        submit_form_obj = SubmitFormDataRequest(form_response)
        submission_dict = submit_form_obj.parse_form_data()
        reason = submit_form_obj.validate_form_data(submission_dict, self.rdb_conn)
        response_id = submit_form_obj.save_data(form_id_ep, submission_dict, mongodb_conn=self.mdb_connect_info)
        self.assertNotEqual(response_id, "")
        mongo_resp = self.data_validator_obj.fetch_form_response(form_id_ep, response_id, rdb_conn=self.rdb_conn, mongodb_conn=self.mdb_connect_info)
        self.assertNotEqual(mongo_resp, {})


    def test_get_form_template(self):
        # Create form with endpoints
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

        template_list = self.data_validator_obj.get_form_template(form_id_ep, self.rdb_conn)
        self.assertNotEqual(len(template_list), 0)
        

    def tearDown(self) -> None:
        sql_utils.clear_db(self.cnx, os.environ.get('RDBSCHEMA', None))
