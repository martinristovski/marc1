from beans.form_data import FormData
import database_services.RDBService as RDBService
import middleware.context as context
from flask import current_app
from database_services.MongoDBTable import MongoDBTable
import utils.rest_utils as RestUtils

class SubmitFormDataRequest:

	def __init__(self, submit_form_request):
		self.form_id = submit_form_request.get("form_id", None)
		self.submission_data = submit_form_request.get("submission_data", None)
		self.table_name = "form_info"


	def validate_data(self):
		if (self.form_id == None) or (self.submission_data == None):
			return False
		
		template = {}
		template['form_id'] = self.form_id
		result = RDBService.find_by_template(context.get_rdb_schema(), self.table_name, template)
		current_app.logger.debug("The value of result is [" + str(result) + "]")
		if result is None:
			return False
		
		return True

	def parse_form_data(self):
		submission_data = self.submission_data
		submission_dict = {}
		for data in submission_data:
			form_data = FormData(data)
			# TODO: Validation of values.
			submission_dict[form_data.field_name] = form_data.field_value
		return submission_dict
	
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