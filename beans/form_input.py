from beans.form_input_elements import FormInputElements
from database_services.RDBService import RDBDataTable
from utils.validator import DataValidator
import middleware.context as md_context


class FormInput:

    def __init__(self, form_object):
        """

        :param form_object: This contains the
          json object submitted by developer
          while creating a form template
        """
        self.inputs = form_object.get("inputs", None)
        self.endpoints = form_object.get("endpoints", None)

    def validate_form_values(self):
        """

        This functions validates if fields(inputs, endpoints)
        are present or not.
        It then checks that each input element provided
        by the end user has a valid
        data type(str, int, float, boolean).

        :return: Empty string if all the fields are valid.
          Else returns the appropriate reason
          to send error_message to the end user
        """
        reason = ""
        data_validator_obj = DataValidator()
        valid_value_type = data_validator_obj.get_all_valid_types()
        if self.inputs is None:
            return "Key input is missing"

        if self.endpoints is None:
            return "Key endpoints is missing"

        for input in self.inputs:
            form_input_elements = FormInputElements(input)
            if (form_input_elements.field_name is None or
               form_input_elements.field_name == ""):

                reason = "One of the input field name is empty"
                return reason

            data_validator_obj = DataValidator()
            input_instance = data_validator_obj.get_value_type(
              form_input_elements.field_type)
            print(input_instance)
            if input_instance is None:
                reason = f"Invalid field_type = {form_input_elements.field_type}\
 received. Valid types={valid_value_type}"
                return reason

        return reason

    def delete_form_record(self, form_id, rdb_conn=md_context.get_rdb_info()):
        """
        This function deletes a form_record from the
        form_info table. This function is used
        when a developer decides to update his form
        template, i.e, add or remove fields
        """
        form_info_db = RDBDataTable(
          "form_info", connect_info=rdb_conn, key_columns=["uuid"])
        template = {}
        template['form_id'] = form_id
        form_info_db.delete(template=template)

    def process_form_creation(
          self, form_id, uuid, rdb_conn=md_context.get_rdb_info()):
        """
        This function creates an entry in form_info table,
        form_column_mapper and
        form_endpoint_mapper. Entries are created
        on the basis of form template
        provided by the developer
        """
        form_info_db = RDBDataTable(
          "form_info", connect_info=rdb_conn, key_columns=["uuid"])

        form_data_info = {}
        form_data_info['form_id'] = form_id
        form_data_info['uuid'] = uuid
        result_list = form_info_db.insert(form_data_info)
        print(result_list)
        form_column_db = RDBDataTable(
          "form_column_mapper",
          connect_info=rdb_conn,
          key_columns=["form_id", "field_name"])
        form_endpoint_db = RDBDataTable(
          "form_endpoint_mapper", connect_info=rdb_conn)

        for input in self.inputs:
            form_input_element = FormInputElements(input)
            form_field_row = {}
            form_field_row['form_id'] = form_id
            form_field_row['field_name'] = form_input_element.field_name
            form_field_row['field_type'] = form_input_element.field_type
            form_field_row['expected_values'] = \
                form_input_element.expected_value
            form_column_record = form_column_db.insert(form_field_row)
            print(form_column_record)

        for endpoint in self.endpoints:
            form_endpoint_row = {}
            form_endpoint_row['form_id'] = form_id
            form_endpoint_row['accepted_endpoints'] = endpoint
            form_endpoint_record = form_endpoint_db.insert(form_endpoint_row)
            print(form_endpoint_record)
