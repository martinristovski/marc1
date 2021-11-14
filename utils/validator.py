from flask import current_app
from database_services.RDBService import RDBDataTable
from database_services.MongoDBTable import MongoDBTable
import middleware.context as md_context
import uuid
import secrets

class DataValidator:

    def __init__(self, rdb_context=None):
        if rdb_context is None:
            self.rdb_context = md_context.get_rdb_info()
        else:
            self.rdb_context = rdb_context

    def get_value_type(s):
        variable_types = [int, float, str, bool]
        string_to_type_dict = {t.__name__: t for t in variable_types}
        return string_to_type_dict[s]

    def generate_uuid_api_key(self):
        dev_uuid = uuid.uuid4()
        api_key = secrets.token_urlsafe(32)

        rdb_data = RDBDataTable('developers', self.rdb_context)
        rdb_data.insert({'uuid': dev_uuid, 'api_key': api_key})
        # RDBDataTable.create('marc1_db', self.context, {'uuid': dev_uuid, 'api_key': api_key})

        return dev_uuid, api_key

    def validate_uuid_api_key(self, uuid, api_key):
        template = {}
        template['uuid'] = uuid
        template['api_key'] = api_key
        response = ""
        rdb_data = RDBDataTable("developers", connect_info=self.rdb_context)
        result = rdb_data.find_by_template(template)
        if len(result) == 0:
            response = f"API KEY={api_key} not associated to Developer={uuid}"

        return response

    def validate_uuid_form_id(self, uuid, form_id):
        template = {}
        template['uuid'] = uuid
        template['form_id'] = form_id
        response = ""

        rdb_data = RDBDataTable("form_info", connect_info=self.context.get_rdb_info(), key_columns=["form_id"])
        result = rdb_data.find_by_template(template)
        if len(result) == 0:
            response = f"Developer={uuid} not associated to form_id={form_id}"

        return response

    def fetch_form_response(self, form_id, response_id=""):
        mongodb_conn = self.context.get_mongo_db_info()
        table_name = str(form_id) + "_" + "response"
        mongo_client = MongoDBTable(table_name, connect_info=mongodb_conn, key_columns=['response_id'])
        template = {}
        mongo_template = {}
        template['form_id'] = form_id
        if not response_id == "":
             mongo_template['response_id'] = response_id

        database_service = RDBDataTable("form_column_mapper", connect_info=self.context.get_rdb_info(), key_columns=["form_id", "field_name"])
        result_list = database_service.find_by_template(template, fields=['field_name'])
        mongo_field_list = []
        mongo_field_list.append('response_id')
        for result in result_list:
            mongo_field_list.append(result['field_name'])

        mongo_resp = mongo_client.find_by_template(mongo_template, field_list=mongo_field_list)
        for response in mongo_resp:
            response.pop("_id")
        return mongo_resp

    def validate_request_endpoint(self, request, form_id):
        template = {}
        template['form_id'] = form_id
        database_service = RDBDataTable("form_endpoint_mapper", connect_info=self.context.get_rdb_info(), key_columns=["form_id"])
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
