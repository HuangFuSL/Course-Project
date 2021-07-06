class NotInitiatedError(BaseException):

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

    def __str__(self):
        return "Engine not initiated"