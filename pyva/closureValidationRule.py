class ClosureValidationRule:

    def __init__(self, calback):
        self.callback = calback
        self.message = None
        self.failed = False

    def passes(self, attribute, value):
        self.callback(attribute, value, self.fail)

        return not self.failed

    def fail(self, message):
        self.failed = True
        self.message = message
