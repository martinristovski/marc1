from flask import Flask, Response, request, jsonify
from flask_cors import CORS
import json
import logging
from datetime import datetime
import uuid
import secrets

import utils.rest_utils as rest_utils

from database_services.RDBService import RDBService as RDBService

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
  api_key = request.headers.get("api_key");

  print("\n DATA: ", data, "\n API_KEY: ", api_key, "\n FORM_TITLE: ", form_title, "\n FORM_INPUTS: ", form_inputs)

  return jsonify(data)

@app.route("/form/", methods=["GET"])
def form_get():
  data = request.get_json()
  form_id = data["form_id"]
  api_key = request.headers.get("api_key");

  # TODO: fetch form from database using form id

  print("FORM_ID: ", form_id, "API_KEY", api_key)
  return jsonify(data)

@app.route("/developer/", methods=["GET"])
def provision_api_key():
  dev_uuid = uuid.uuid4()
  api_key = secrets.token_urlsafe(32)

  print("UUID: ", dev_uuid, "API_KEY: ", api_key)

  return jsonify({"api_key": api_key, "uuid": dev_uuid})

@app.route("/form-submission/", methods=["POST"])
def submit_form_entry():
  data = request.get_json()
  form_id = data["form_id"]
  submission_data = data["submission_data"]

  # TODO: save submission data associated with form into mongo table

  print("FORM_ID: ", form_id, "SUBMISSION_DATA", submission_data)

  return jsonify(data)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
