from database_services.RDBService import RDBDataTable
from beans.form_input import FormInput
import uuid
import secrets


# Helper functions
def create_form_helper(form_input, uuid, rdb_conn):
    form_id = secrets.token_urlsafe(32)
    form_creation_request = FormInput(form_input)
    reason = form_creation_request.validate_form_values()
    if reason != "":
        return Error.bad_request(message=reason)

    form_creation_request.process_form_creation(form_id=form_id, uuid=uuid, rdb_conn=rdb_conn)

    return form_id, reason


class Request():

    def __init__(self, headers):
        self.headers = headers