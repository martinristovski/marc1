from beans.form_data import FormData
from database_services.RDBService import RDBDataTable
import middleware.context as context
from flask import current_app
from database_services.MongoDBTable import MongoDBTable
import utils.rest_utils as RestUtils
from utils.validator import DataValidator

class SubmitFormDataRequest:

	def __init__(self, submit_form_request):
		self.form_id = submit_form_request.get("form_id", None)
		self.submission_data = submit_form_request.get("submission_data", None)
		self.table_name = "form_info"


	def validate_form_request(self):
		if (self.form_id == None) or (self.submission_data == None):
			return False
		
		template = {}
		template['form_id'] = self.form_id
		database_service = RDBDataTable("form_info", connect_info=context.get_rdb_info(), key_columns=["form_id"])
		result = database_service.find_by_template(template)
		current_app.logger.debug("The value of result is [" + str(result) + "]")
		if result is None:
			return False
		
		return True

	def parse_form_data(self):
		submission_data = self.submission_data
		submission_dict = {}
		for data in submission_data:
			form_data = FormData(data)
			submission_dict[form_data.field_name] = form_data.field_value
		return submission_dict

	def validate_form_data(self, submitted_dict):
		template = {}
		template['form_id'] = self.form_id
		submitted_keys = submitted_dict.keys()
		expected_type_dict = {}
		expected_value_dict = {}
		database_service = RDBDataTable("form_column_mapper", connect_info=context.get_rdb_info(), key_columns=["form_id", "field_name"])
		result_list = database_service.find_by_template(template, fields=['field_name', 'field_type','expected_values'])
		if result_list is not None:
			for row in result_list:
				expected_type_dict[row['field_name']] = row['field_type']
				expected_value_list = []
				if row['expected_values'] is not None:
					expected_value_list = list(expected_value_list)
				expected_value_dict[row['field_name']] = expected_value_list
		else:
			reason = f"No attribute configured for form_id={self.form_id}"
			return reason

		expected_key_list = expected_type_dict.keys()
		missing_keys = list(set(expected_key_list) - set(submitted_keys))
		if len(missing_keys) == 0:
			for key, value in submitted_dict.items():
				expected_type = DataValidator.get_value_type(expected_type_dict[key])
				received_type = type(value)
				# print("Expected type: " + str(expected_type))
				# print("Received type: " + str(expected_type))
				instance_state = isinstance(value, expected_type)
				print("Instance: " + str(instance_state))
				if not instance_state is True:
					reason = f"For field={key}, expected ={expected_type.__name__}, received={received_type.__name__}"
					return reason
				
				expected_values = expected_value_dict[key]
				print("Expected values :" + str(expected_values))
				if not len(expected_values)==0 and value not in expected_values:
					reason = f"Expected={expected_values}, got ={value}"
					return reason
		else:
			
			reason = f"Missing fields={','.join(str(mkeys) for mkeys in missing_keys)} in the request. Please fill the form"
			return reason

		return ""

	
	def save_data(self, form_id, data):
		mongodb_conn = context.get_mongo_db_info()
		table_name = self.get_table_name(form_id)
		response_id = RestUtils.id_generator(size=32)
		data['response_id'] = response_id
		mongo_client = MongoDBTable(table_name, connect_info=mongodb_conn, key_columns=['response_id'])
		insert_id = mongo_client.insert(data)
		current_app.logger.info(f"Data inserted with id ={insert_id}")
		return response_id


	def get_table_name(self, form_id):
		return str(form_id) + "_" + "response"