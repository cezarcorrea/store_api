class BaseException(Exception):
    message: str = "Internal Server Error"

    def __init__(self, message: str | None = None) -> None:
        if message:
            self.message = message
        super().__init__(self.message)


class NotFoundException(BaseException):
    message = "Not Found"


class InsertionException(BaseException):
    message = "Error inserting data"
