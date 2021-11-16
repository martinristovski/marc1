class FormData:

    def __init__(self, form_object):
        """
        :param form_object: This contains a single
          element of form_data submitted by end user
        """
        self.field_name = form_object.get("field_name", None)
        self.field_value = form_object.get("field_value", None)
