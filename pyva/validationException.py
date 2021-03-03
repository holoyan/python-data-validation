class ValidationException(Exception):

    def __init__(self, validator, message="The given data was invalid."):
        self.validator = validator
        self.message = message
        super().__init__(self.message)
