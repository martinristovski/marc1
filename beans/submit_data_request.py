from beans.form_data import FormData
from database_services.RDBService import RDBDataTable
import middleware.context as context
from flask import current_app
from database_services.MongoDBTable import MongoDBTable
import utils.rest_utils as RestUtils
from utils.validator import DataValidator


class SubmitFormDataRequest:

	def __init__(self, submit_form_request):
		"""
		:param form_object: This contains the json object submitted by user 
		when saving their data into our application.
		"""
		self.form_id = submit_form_request.get("form_id", None)
		self.submission_data = submit_form_request.get("submission_data", None)
		self.table_name = "form_info"

	def validate_form_request(self, rdb_conn=context.get_rdb_info()):
		"""
		This function validates if the form_id and submission data 
		received in the request is present in our database or not.
		:return: False if no record exists for the form_id provided else True
		"""
		if (self.form_id is None) or (self.submission_data is None):
			return False
		
		template = {'form_id': self.form_id}
		database_service = RDBDataTable("form_info", connect_info=rdb_conn, key_columns=["form_id"])
		result = database_service.find_by_template(template)
		current_app.logger.debug("The value of result is [" + str(result) + "]")
		if result is None:
			return False
		
		return True

	def parse_form_data(self):
		"""
		This function converts the request received to dict to be saved
		in MongoDB.
		:return: Returns the dictionary converted to be saved in MongoDB
		"""
		submission_data = self.submission_data
		submission_dict = {}
		for data in submission_data:
			form_data = FormData(data)
			submission_dict[form_data.field_name] = form_data.field_value
		return submission_dict

	def validate_form_data(self, submitted_dict, rdb_conn=context.get_rdb_info()):
		"""
		This function validates if the submitted data is inline with
		the template created by the developer. It checks the fields submitted
		and the type of data received in the submitted value.
		:return: Empty string if fields are valid, else returns the appropriate
		error message.
		"""
		template = {}
		template['form_id'] = self.form_id
		submitted_keys = submitted_dict.keys()
		expected_type_dict = {}
		expected_value_dict = {}
		database_service = RDBDataTable("form_column_mapper", connect_info=rdb_conn, key_columns=["form_id", "field_name"])
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

	def save_data(self, form_id, data, mongodb_conn=context.get_mongo_db_info()):
		"""
		:param form_id: form_id for which the response has to be saved.
		:param data: The data to be saved in the mongoDB.
		:param mongodb_conn: mongodb connection info
		This functions saves the data in the mongoDB database.
		:returns: response_id of the response submitted.
		"""
		table_name = self.get_table_name(form_id)
		response_id = RestUtils.id_generator(size=32)
		data['response_id'] = response_id
		mongo_client = MongoDBTable(table_name, connect_info=mongodb_conn, key_columns=['response_id'])
		insert_id = mongo_client.insert(data)
		current_app.logger.info(f"Data inserted with id ={insert_id}")
		return response_id


	def get_table_name(self, form_id):
		"""
		:param form_id: form_id for which the response has to be saved.
		:returns: mongodb table name
		"""
		return str(form_id) + "_" + "response"