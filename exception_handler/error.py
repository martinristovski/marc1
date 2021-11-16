from flask import jsonify


def bad_request(message):
    """
    :param message: Message to be provied to the end user.
    This function returns a template response for 400 status code.
    :return: response to return the end user.
    """
    response = jsonify({'error': 'bad request', 'message': message})
    response.status_code = 400
    return response


def unauthorized(message):
    """
    :param message: Message to be provied to the end user.
    This function returns a template response for 400 status code.
    :return: response to return the end user.
    """
    response = jsonify({'error': 'unauthorized', 'message': message})
    response.status_code = 401
    return response


def forbidden(message):
    """
    :param message: Message to be provied to the end user.
    This function returns a template response for 403 status code.
    :return: response to return the end user.
    """
    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403
    return response


def resouce_already_exists(message):
    """
    :param message: Message to be provied to the end user.
    This function returns a template response for 409 status code.
    :return: response to return the end user.
    """
    response = jsonify({'error': 'resouce_already_exists', 'message': message})
    response.status_code = 409
    return response


def resource_not_found(message):
    """
    :param message: Message to be provied to the end user.
    This function returns a template response for 404 status code.
    :return: response to return the end user.
    """
    response = jsonify({'error': 'resource_not_found', 'message': message})
    response.status_code = 404
    return response


def internal_server_error(message):
    """
    :param message: Message to be provied to the end user.
    This function returns a template response for 500 status code.
    :return: response to return the end user.
    """
    response = jsonify(
        {'error': 'We are facing some technical difficulties.  \
        Please try after sometime.', 'message': message})
    response.status_code = 500
    return response
