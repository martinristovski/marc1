from beans.form_input import FormInput
from beans.submit_data_request import SubmitFormDataRequest
import secrets


# Helper functions
def create_form_helper(form_input, uuid, rdb_conn):
    form_id = secrets.token_urlsafe(32)
    form_creation_request = FormInput(form_input)
    reason = form_creation_request.validate_form_values()
    if reason != "":
        return "Error! " + reason

    form_creation_request.process_form_creation(
        form_id=form_id, uuid=uuid, rdb_conn=rdb_conn)

    return form_id, reason


def submit_form_response(response_input, form_id):
    submit_data_obj = SubmitFormDataRequest(response_input)
    

class Request():

    def __init__(self, headers):
        self.headers = headers
