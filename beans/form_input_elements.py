from flask import current_app

class FormInputElements:

	def __init__(self, form_object):
		self.field_name = form_object.get("field_name", None)
		self.field_type = form_object.get("field_type", None)
		self.expected_value = form_object.get("expected_values", "")

	
