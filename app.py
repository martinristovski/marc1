from flask import Flask, Response, request, jsonify, current_app
from flask_cors import CORS
import json
import logging
from datetime import datetime
import uuid
import secrets

from utils.validator import DataValidator
from beans.submit_data_request import SubmitFormDataRequest
from beans.form_input import FormInput
import exception_handler.error as Error

from database_services.RDBService import RDBDataTable
import middleware.context as context

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

application = Flask(__name__)
CORS(application)


# This path simply echoes to check that the app is working.
# The path is /health and the only method is GET
@application.route("/health", methods=["GET"])
def health_check():
    rsp_data = {"status": "healthy", "time": str(datetime.now())}
    rsp_str = json.dumps(rsp_data)
    rsp = Response(rsp_str, status=200, content_type="app/json")
    return rsp


# This path allows developers to submit a form template
# The path is /developer/<uuid>/create_form and the only method is POST
@application.route("/developer/<uuid>/create_form", methods=["POST"])
def form_create(uuid):
    try:
        if request.data:
            api_key = request.headers.get("API-KEY", None)
            if api_key is None:
                return Error.forbidden(message="\
                No API KEY provided to access the API.")

            api_key_resp = DataValidator.validate_uuid_api_key(uuid, api_key)

            if api_key_resp != "":
                return Error.unauthorized(message=api_key_resp)

            form_id = secrets.token_urlsafe(32)
            form_creation_request = FormInput(request.get_json())
            reason = form_creation_request.validate_form_values()
            if reason != "":
                return Error.bad_request(message=reason)

            form_creation_request.process_form_creation(
                form_id=form_id, uuid=uuid)
            response_json = {}
            response_json["form_id"] = form_id
            response_json["msg"] = "Form Created Successfully"
            return jsonify(response_json), 201
        else:
            return Error.bad_request(message='Invalid request format')
    except Exception:
        current_app.logger.exception(
            "Exception occured while processing function: form_create")
        return Error.internal_server_error("Internal server error")


# This path allows developers to get list of all forms created by them
# The path is /developer/<uuid>/form and the only method is GET
@application.route("/developer/<uuid>/form", methods=["GET"])
def get_users_forms(uuid):
    api_key = request.headers.get("API-KEY", None)
    if api_key is None:
        return Error.forbidden(
            message="No API KEY provided to access the API.")

    api_key_resp = DataValidator.validate_uuid_api_key(uuid, api_key)

    if api_key_resp != "":
        return Error.unauthorized(message=api_key_resp)

    form_list = DataValidator.get_all_users_form(uuid=uuid)
    return jsonify(forms=form_list), 200


# This path allows developers to get list of all forms created by them
# The path is /developer/<uuid>/form and the only method is GET
@application.route("/developer/register", methods=["GET"])
def provision_api_key():
    try:
        dev_uuid = uuid.uuid4()
        api_key = secrets.token_urlsafe(32)
        row = {}
        row['uuid'] = dev_uuid
        row['api_key'] = api_key
        database_service = RDBDataTable(
            "developer_info",
            connect_info=context.get_rdb_info(),
            key_columns=["uuid"])
        database_service.insert(row)
        response_json = {}
        response_json['API-KEY'] = api_key
        response_json['uuid'] = dev_uuid
        return jsonify(response_json), 201
    except Exception:
        current_app.logger.exception(
            "Exception occured while processing function: submit_form_entry")
        return Error.internal_server_error("Internal server error")


# This path saves the data submitted by user to the form developers created
# The path is /user/submit_form and the only method is POST
@application.route("/user/submit_form", methods=["POST"])
def submit_form_entry():
    try:
        if request.data:
            data = SubmitFormDataRequest(request.get_json())
            if not data.validate_form_request():
                return Error.bad_request(message='Mandatory Parameter missing')

            if (not DataValidator.validate_request_endpoint(
                    request, data.form_id)):
                return Error.forbidden(
                    message="Request received from different endpoint.")

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
        current_app.logger.exception(
            "Exception occured while processing function: submit_form_entry")
        return Error.internal_server_error("Internal server error")


# This path allows developers to update
# the form template for a particular form_id
# The path is /developer/<uuid>/<form_id>/ and the only method is PUT
@application.route("/developer/<uuid>/<form_id>/", methods=["PUT"])
def update_existing_form(uuid, form_id):
    try:
        api_key = request.headers.get("API-KEY", None)
        if api_key is None:
            return Error.forbidden(
                message="No API KEY provided to access the API.")
        api_key_resp = DataValidator.validate_uuid_api_key(uuid, api_key)
        if api_key_resp != "":
            return Error.unauthorized(message=api_key_resp)
        api_key_resp = DataValidator.validate_uuid_form_id(uuid, form_id)
        if api_key_resp != "":
            return Error.unauthorized(message=api_key_resp)

        form_creation_request = FormInput(request.get_json())
        reason = form_creation_request.validate_form_values()
        if reason != "":
            return Error.bad_request(message=reason)

        form_creation_request.delete_form_record(form_id)
        form_creation_request.process_form_creation(form_id=form_id, uuid=uuid)
        response_json = {}
        response_json["form_id"] = form_id
        response_json["msg"] = "Form Created Successfully"
        return jsonify(response_json), 201

    except Exception:
        current_app.logger.exception(
            "Exception occured while processing function: get_batch_response")
        return Error.internal_server_error("Internal server error")


# This path allows developers to get all the
# responses associated with a form_id
# The path is
# /developer/<uuid>/<form_id>/response and the only method is GET
@application.route("/developer/<uuid>/<form_id>/response", methods=["GET"])
def get_batch_response(uuid, form_id):
    try:
        api_key = request.headers.get("API-KEY", None)
        if api_key is None:
            return Error.forbidden(
                message="No API KEY provided to access the API.")
        api_key_resp = DataValidator.validate_uuid_api_key(uuid, api_key)
        if api_key_resp != "":
            return Error.unauthorized(message=api_key_resp)
        api_key_resp = DataValidator.validate_uuid_form_id(uuid, form_id)
        if api_key_resp != "":
            return Error.unauthorized(message=api_key_resp)
        form_response = DataValidator.fetch_form_response(form_id)
        return jsonify(form_response), 200

    except Exception:
        current_app.logger.exception(
            "Exception occured while processing function: get_batch_response")
        return Error.internal_server_error("Internal server error")


@application.route("/developer/<form_id>/get_template", methods=["GET"])
def get_form_template(form_id):
    try:
        form_response = DataValidator.get_form_template(form_id)
        return jsonify(template=form_response), 200

    except Exception:
        current_app.logger.exception(
            "Exception occured while processing function: get_batch_response")
        return Error.internal_server_error("Internal server error")


# This path allows developers to get
# a particular response submitted to a form_id
# The path is
# /developer/<uuid>/<form_id>/response/<response_id>
# and the only method is GET
@application.route(
    "/developer/<uuid>/<form_id>/response/<response_id>", methods=["GET"])
def get_single_response(uuid, form_id, response_id):
    try:
        api_key = request.headers.get("API-KEY", None)
        if api_key is None:
            return Error.forbidden(
                message="No API KEY provided to access the API.")

        api_key_resp = DataValidator.validate_uuid_api_key(uuid, api_key)

        if api_key_resp != "":
            return Error.unauthorized(message=api_key_resp)

        api_key_resp = DataValidator.validate_uuid_form_id(uuid, form_id)

        if api_key_resp != "":
            return Error.unauthorized(message=api_key_resp)

        form_response = DataValidator.fetch_form_response(form_id, response_id)

        return jsonify(form_response), 200

    except Exception:
        current_app.logger.exception(
            "Exception occured while processing function: get_batch_response")
        return Error.internal_server_error("Internal server error")


if __name__ == '__main__':
    application.run(host="0.0.0.0", port=5000)
