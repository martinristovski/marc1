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
  form_title = data["title"]
  form_inputs = data["inputs"]
  api_key = request.headers.get("api_key")

  print("\n DATA: ", data, "\n API_KEY: ", api_key, "\n FORM_TITLE: ", form_title, "\n FORM_INPUTS: ", form_inputs)

  return jsonify(data)

@app.route("/form/", methods=["GET"])
def form_get():
  data = request.get_json()
  form_id = data["form_id"]
  api_key = request.headers.get("api_key")

  # TODO: fetch form from database using form id

  print("FORM_ID: ", form_id, "API_KEY", api_key)
  return jsonify(data)

@app.route("/developer/", methods=["GET"])
def provision_api_key():
  dev_uuid = uuid.uuid4()
  api_key = secrets.token_urlsafe(32)

  print("UUID: ", dev_uuid, "API_KEY: ", api_key)

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
            return jsonify(response_json)
        else:
            return Error.bad_request(message='Invalid request format')
    except Exception:
        current_app.logger.exception("Exception occured while processing function: submit_form_entry")
        return Error.internal_server_error("Internal server error")



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
