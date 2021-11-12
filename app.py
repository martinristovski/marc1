from flask import Flask, Response, request, jsonify, current_app
from flask_cors import CORS
import json
import logging
from datetime import datetime
import uuid
import secrets

import utils.rest_utils as rest_utils
from utils.validator import DataValidator
from beans.submit_data_request import SubmitFormDataRequest
import exception_handler.error as Error

from database_services.RDBService import RDBService as RDBService
from database_services.queries import get_form_data

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)
CORS(app)

##################################################################################################################

# This path simply echoes to check that the app is working.
# The path is /health and the only method is GETs
@app.route("/health", methods=["GET"])
def health_check():
    rsp_data = {"status": "healthy", "time": str(datetime.now())}
    rsp_str = json.dumps(rsp_data)
    rsp = Response(rsp_str, status=200, content_type="app/json")
    return rsp

@app.route("/form/", methods=["POST"])
def form_create():
  data = request.get_json()
  form_inputs = data["inputs"]
  api_key = request.headers.get("api_key")

  # get dev uuid
  developer_records = RDBService.get_by_prefix('marc1_db', 'developers', 'api_key', api_key)

  uuid = None
  if len(developer_records) == 1:
    uuid = developer_records[0]['uuid']
  else:
    # TODO: error
    pass

  form_record = RDBService.insert_and_return('marc1_db', 'forms', {'uuid': uuid})[0]

  if not form_record:
    # TODO: error
    pass

  print("=============")
  print(form_record)

  for form_input in form_inputs:
    print(form_input)
    RDBService.create('marc1_db', 'form_info', {'form_id': form_record['LAST_INSERT_ID()'], 'col': form_input['col'], 'col_type': form_input['col_type']})


  return jsonify(data)

@app.route("/form/", methods=["GET"])
def form_get():
  data = request.get_json()
  form_id = data["form_id"]
  api_key = request.headers.get("api_key")

  form_submissions = {}
  # make sure form belongs to developer
  records = get_form_data(form_id)

  for record in records:
    form_sub_id = record['form_submission_id']
    if form_sub_id not in form_submissions:
      form_submissions[form_sub_id] = {}

    form_submissions[form_sub_id][record['col']] = record['col_val']

  return jsonify(form_submissions)

@app.route("/developer/", methods=["GET"])
def provision_api_key():
  dev_uuid = uuid.uuid4()
  api_key = secrets.token_urlsafe(32)

  RDBService.create('marc1_db', 'developers', {'uuid': dev_uuid, 'api_key': api_key})
  return jsonify({"api_key": api_key, "uuid": dev_uuid})

@app.route("/user/submit_form", methods=["POST"])
def submit_form_entry():
    try:
        if request.data:
            data = SubmitFormDataRequest(request.get_json())
            if not data.validate_form_request():
                return Error.bad_request(message='Mandatory Parameter missing')

            if not DataValidator.validate_request_endpoint(request, data.form_id):
                return Error.forbidden(message="Request received from different endpoint.")

            data_dict = data.parse_form_data()
            reason = data.validate_form_data(data_dict)
            if reason != "":
                return Error.bad_request(message=reason)
            response_id = data.save_data(form_id=data.form_id, data=data_dict)

            response_json = {}
            response_json['response_id'] = response_id
            response_json['msg'] = "Successfully saved"
            return jsonify(response_json), 201
        else:
            return Error.bad_request(message='Invalid request format')
    except Exception:
        current_app.logger.exception("Exception occured while processing function: submit_form_entry")
        return Error.internal_server_error("Internal server error")

@app.route("/developer/<uuid>/<form_id>/response", methods=["GET"])
def get_batch_response(uuid, form_id):
    try:
        api_key = request.headers.get("API-KEY", None)
        if api_key is None:
            return Error.forbidden(message="No API KEY provided to access the API.")

        api_key_resp = DataValidator.validate_uuid_api_key(uuid, api_key)

        if api_key_resp != "":
            return Error.unauthorized(message=api_key_resp)

        api_key_resp = DataValidator.validate_uuid_form_id(uuid, form_id)

        if api_key_resp != "":
            return Error.unauthorized(message=api_key_resp)

        form_response = DataValidator.fetch_form_response(form_id)

        return jsonify(form_response), 201
        
    except Exception:
        current_app.logger.exception("Exception occured while processing function: get_batch_response")
        return Error.internal_server_error("Internal server error")

@app.route("/developer/<uuid>/<form_id>/response/<response_id>", methods=["GET"])
def get_single_response(uuid, form_id, response_id):
    try:
        api_key = request.headers.get("API-KEY", None)
        if api_key is None:
            return Error.forbidden(message="No API KEY provided to access the API.")

        api_key_resp = DataValidator.validate_uuid_api_key(uuid, api_key)

        if api_key_resp != "":
            return Error.unauthorized(message=api_key_resp)

        api_key_resp = DataValidator.validate_uuid_form_id(uuid, form_id)

        if api_key_resp != "":
            return Error.unauthorized(message=api_key_resp)

        form_response = DataValidator.fetch_form_response(form_id, response_id)

        return jsonify(form_response), 201
        
    except Exception:
        current_app.logger.exception("Exception occured while processing function: get_batch_response")
        return Error.internal_server_error("Internal server error")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
