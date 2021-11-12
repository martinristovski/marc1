from flask import current_app
from database_services.RDBService import RDBDataTable
import middleware.context as context


class DataValidator:
	
	def get_value_type(s):
		variable_types = [int, float, str, bool]
		string_to_type_dict = {t.__name__: t for t in variable_types}
		return string_to_type_dict[s]
		

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
