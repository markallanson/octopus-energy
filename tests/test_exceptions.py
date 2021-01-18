from unittest import TestCase
from unittest.mock import Mock

from octopus_energy.exceptions import ApiError, ApiBadRequestError


class ApiErrorTestCase(TestCase):
    def test_error(self):
        response = Mock()
        message = "Message"
        response.status = 500
        response.text = message
        with self.subTest("response"):
            try:
                raise ApiError(response, message)
            except ApiError as e:
                self.assertEqual(e.response, response)
        with self.subTest("message"):
            try:
                raise ApiError(response, message)
            except ApiError as e:
                self.assertEqual(e.message, message)
        with self.subTest("__str__"):
            try:
                raise ApiError(response, message)
            except ApiError as e:
                self.assertIn(message, str(e))
                self.assertIn("500", str(e))


class ApiBadRequestErrorTestCase(TestCase):
    def test_error(self):
        response = Mock()
        with self.subTest("response"):
            try:
                raise ApiBadRequestError(response)
            except ApiError as e:
                self.assertEqual(e.response, response)
