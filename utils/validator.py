from re import template
from flask import current_app, url_for
from database_services.RDBService import RDBDataTable
import middleware.context as context
from database_services.MongoDBTable import MongoDBTable

class DataValidator:
	
	def get_all_valid_types():
		variable_types = [int, float, str, bool]
		return variable_types

	def get_value_type(s):
		variable_types = DataValidator.get_all_valid_types()
		string_to_type_dict = {t.__name__: t for t in variable_types}
		for key,value in string_to_type_dict.items():
			if s == key:
				return value	
		return None
		 
		
	def get_all_users_form(uuid):
		form_list_resp = []
		form_info_db = RDBDataTable("form_info", connect_info=context.get_rdb_info(), key_columns=["uuid"])
		template = {}
		template['uuid'] = uuid
		form_list = form_info_db.find_by_template(template, fields=['form_id'])
		if len(form_list) != 0:
			for forms in form_list:
				print(url_for('get_batch_response', uuid=uuid, form_id=forms['form_id']))
				form_list_resp.append(url_for('get_batch_response', uuid=uuid, form_id=forms['form_id']))
		
		return form_list_resp

	def validate_uuid_api_key(uuid, api_key):
		template = {}
		template['uuid'] = uuid
		template['api_key'] = api_key
		response = ""
		database_service = RDBDataTable("developer_info", connect_info=context.get_rdb_info(), key_columns=["form_id"])
		result = database_service.find_by_template(template)
		if len(result) == 0:
			response = f"API KEY={api_key} not associated to Developer={uuid}"

		return response

	def validate_uuid_form_id(uuid, form_id):
		template = {}
		template['uuid'] = uuid
		template['form_id'] = form_id
		response = ""
		database_service = RDBDataTable("form_info", connect_info=context.get_rdb_info(), key_columns=["form_id"])
		result = database_service.find_by_template(template)
		if len(result) == 0:
			response = f"Developer={uuid} not associated to form_id={form_id}"

		return response

	def fetch_form_response(form_id, response_id=""):
		mongodb_conn = context.get_mongo_db_info()
		table_name = str(form_id) + "_" + "response"
		mongo_client = MongoDBTable(table_name, connect_info=mongodb_conn, key_columns=['response_id'])
		template = {}
		mongo_template = {}
		template['form_id'] = form_id
		if not response_id == "":
			 mongo_template['response_id'] = response_id
		database_service = RDBDataTable("form_column_mapper", connect_info=context.get_rdb_info(), key_columns=["form_id", "field_name"])
		result_list = database_service.find_by_template(template, fields=['field_name'])
		mongo_field_list = []
		mongo_field_list.append('response_id')
		for result in result_list:
			mongo_field_list.append(result['field_name'])
		
		mongo_resp = mongo_client.find_by_template(mongo_template, field_list=mongo_field_list)
		for response in mongo_resp:
			response.pop("_id")
		return mongo_resp

	def validate_request_endpoint(request, form_id):
		template = {}
		template['form_id'] = form_id
		database_service = RDBDataTable("form_endpoint_mapper", connect_info=context.get_rdb_info(), key_columns=["form_id"])
		result = database_service.find_by_template(template, fields=['accepted_endpoints'])
		endpoint_list = []
		# print(request.headers)
		referrer = request.headers.get("Referrer", None)
		if referrer is None:
			return False

		print(f"The value of result={result}")
		if len(result) != 0:
			for row in result:
				endpoint_list.append(row['accepted_endpoints'])
		else:
			return False
		

		if referrer in endpoint_list:
			return True
		else:
			return False
