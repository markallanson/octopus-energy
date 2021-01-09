class ApiError(Exception):
    """An error has occurred while calling the octopus energy API"""

    def __init__(self, response, message="") -> None:
        self.response = response
        self.message = message

    def __str__(self) -> str:
        return f"{self.response.status} - {self.response.text}"


class ApiAuthenticationError(Exception):
    """The credentials were rejected by Octopus."""

    pass


class ApiBadRequestError(Exception):
    """Data posted to an API is incorrect. Typically the response code was 400."""

    pass


class ApiNotFoundError(Exception):
    """The resource requested as part of an API call does not exist."""

    pass
