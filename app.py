from flask import Flask, Response, request, jsonify
from flask_cors import CORS
import json
import logging
from datetime import datetime
import uuid
import secrets

import utils.rest_utils as rest_utils

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
  api_key = request.headers.get("api_key");

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
  api_key = request.headers.get("api_key");

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

@app.route("/form-submission/", methods=["POST"])
def submit_form_entry():
  data = request.get_json()
  form_id = data["form_id"]
  submission_data = data["submission_data"]

  form_submission_id = RDBService.insert_and_return('marc1_db', 'form_submission', {'form_id': form_id})[0]["LAST_INSERT_ID()"]

  for col in submission_data:
    RDBService.create('marc1_db', 'form_submission_field_entry', {'form_submission_id': form_submission_id, 'col': col, 'col_val': submission_data[col]})

  return jsonify(data)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
