from unittest import TestCase

from RequestProcessor.views import validate


class Test(TestCase):
    def test_validate_missing_fields(self):
        data = '{"customerID":1,"tagID":2,"userID":"aaaaaaaa-bbbb-cccc-1111-222222222222","remoteIP":"123.234.56.78"}'
        self.assertFalse(validate(data))

    def test_validate_valid(self):
        data = '{"customerID":1,"tagID":2,"userID":"aaaaaaaa-bbbb-cccc-1111-222222222222","remoteIP":"123.234.56.78","timestamp":1500000000}'
        self.assertTrue(validate(data))

    def test_validate_invalidjson(self):
        data = '"customerID": 12, "tagId'
        self.assertFalse(validate(data))
