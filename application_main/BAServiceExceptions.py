class BAServiceError(Exception):
    status_code = 500

    def __init__(self, message, status_code=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):
        error_dict = {}
        error_dict['message'] = self.message
        error_dict['status'] = self.status_code
        return error_dict
