from flask import url_for
from database_services.RDBService import RDBDataTable
import middleware.context as md_context
from database_services.MongoDBTable import MongoDBTable


class DataValidator:

    def __init__(self) -> None:
        pass

    def get_all_valid_types(self):
        """
        This function returns the list of valid data types allowed in the
        fields of form templates.
        :return: list of data_types
        """
        variable_types = [int, float, str, bool]
        return variable_types

    def get_value_type(self, s):
        """
        :param s: String type of the class to be found
        This function returns the list of valid data types allowed in the
        fields of form templates.
        :return: list of data_types
        """
        variable_types = self.get_all_valid_types()
        string_to_type_dict = {t.__name__: t for t in variable_types}
        for key, value in string_to_type_dict.items():
            if s == key:
                return value
        return None

    def get_all_users_form(self, uuid, rdb_conn=md_context.get_rdb_info()):
        """
        :param uuid: Unique Identifier of the user
        :param rdb_conn: Relational database connection context.
        This function returns the list of forms created by user and creates
        a list of urls to access response associated with them.
        :return form_list_resp: List of urls containing path to response API.
        """
        form_list_resp = []
        form_info_db = RDBDataTable(
            "form_info",
            connect_info=rdb_conn,
            key_columns=["uuid"])
        template = {}
        template['uuid'] = uuid
        form_list = form_info_db.find_by_template(template, fields=['form_id'])
        if len(form_list) != 0:
            for forms in form_list:
                form_list_resp.append(
                    url_for(
                        'get_batch_response',
                        uuid=uuid,
                        form_id=forms['form_id']))

        return form_list_resp

    def validate_uuid_api_key(
            self, uuid, api_key, rdb_conn=md_context.get_rdb_info()):
        """
        :param uuid: Unique Identifier of the user
        :param api_key: API KEY provided to the user
        :param rdb_conn: Relational database connection context.
        This function checks if the combination of API-KEY and uuid
        provided in the requests is valid or not
        :return response: Empty String if they are valid,
                        else returns correct error message.
        """
        template = {}
        template['uuid'] = uuid
        template['api_key'] = api_key
        response = ""
        database_service = RDBDataTable(
            "developer_info",
            connect_info=rdb_conn,
            key_columns=["form_id"])
        result = database_service.find_by_template(template)
        if len(result) == 0:
            response = f"API KEY={api_key} not associated to Developer={uuid}"

        return response

    def validate_uuid_form_id(
            self, uuid, form_id, rdb_conn=md_context.get_rdb_info()):
        """
        :param uuid: Unique Identifier of the user
        :param form_id: form_id for which the request is being processed
        :param rdb_conn: Relational database connection context.
        This function checks if the combination of form_id and uuid are valid
        or not.
        :return response: Empty string if its valid else appropriate error
        message.
        """
        template = {}
        template['uuid'] = uuid
        template['form_id'] = form_id
        response = ""
        database_service = RDBDataTable(
            "form_info", connect_info=rdb_conn, key_columns=["form_id"])
        result = database_service.find_by_template(template)
        if len(result) == 0:
            response = f"Developer={uuid} not associated to form_id={form_id}"

        return response

    def fetch_form_response(self, form_id, response_id="",
                            rdb_conn=md_context.get_rdb_info(),
                            mongodb_conn=md_context.get_mongo_db_info()):
        """
        :param form_id: form_id for which the results have to be fetched.
        :param response_id: Response id if to fetch a particular response
        else empty.
        :param rdb_conn: Relational database connection context.
        :param mongodb_conn: MongoDB connection context.
        This function hits the mongoDB database and fetches the response
        to be provied to the end user.
        :return mongo_resp: Response saved in the mongoDB.
        """
        table_name = str(form_id) + "_" + "response"
        mongo_client = MongoDBTable(
            table_name,
            connect_info=mongodb_conn,
            key_columns=['response_id'])

        template = {}
        mongo_template = {}
        template['form_id'] = form_id
        if not response_id == "":
            mongo_template['response_id'] = response_id

        database_service = RDBDataTable(
            "form_column_mapper", connect_info=rdb_conn,
            key_columns=["form_id", "field_name"])
        result_list = database_service.find_by_template(
            template, fields=['field_name'])
        mongo_field_list = []
        mongo_field_list.append('response_id')
        for result in result_list:
            mongo_field_list.append(result['field_name'])

        mongo_resp = mongo_client.find_by_template(
            mongo_template, field_list=mongo_field_list)
        for response in mongo_resp:
            response.pop("_id")
        return mongo_resp

    def get_form_template(
            self, form_id, rdb_conn=md_context.get_rdb_info()):
        """
        :param form_id: Form_id for the template
        :param rdb_conn: Relational database connection context.
        """
        template = {}
        template_list = []
        template['form_id'] = form_id
        database_service = RDBDataTable(
            "form_column_mapper", connect_info=rdb_conn,
            key_columns=["form_id"])
        result = database_service.find_by_template(
            template, fields=['field_name, field_type, expected_values'])
        if len(result) != 0:
            for ele in result:
                template_list.append(ele)

        return template_list

    def validate_request_endpoint(
            self, request, form_id, rdb_conn=md_context.get_rdb_info()):
        """
        :param request: Flask request object
        :param form_id: Form_id for the request received
        :param rdb_conn: Relational database connection context.
        This function validates if the request is received from the configured
        endpoint.
        :return: True if the request is comming from configured endpoint.
        Else False.
        """
        template = {}
        template['form_id'] = form_id
        database_service = RDBDataTable(
            "form_endpoint_mapper", connect_info=rdb_conn,
            key_columns=["form_id"])
        result = database_service.find_by_template(
            template, fields=['accepted_endpoints'])
        endpoint_list = []
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
