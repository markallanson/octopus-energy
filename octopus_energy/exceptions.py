class ApiError(Exception):
    """An error has occurred while calling the octopus energy API"""

    def __init__(self, *args: object, response) -> None:
        super().__init__(*args)
        self.response = response

    def __str__(self) -> str:
        return f"{self.response.status} - {self.response.text}"


class ApiAuthenticationError(Exception):
    """The credentials were rejected by Octopus."""

    ...
