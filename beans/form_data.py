from flask import current_app

class FormData:

	def __init__(self, form_object):
		self.field_name = form_object.get("field_name", None)
		self.field_value = form_object.get("field_value", None)


	def validate_form_data(self, current_type, expected_type):
		return current_type == expected_type

	
