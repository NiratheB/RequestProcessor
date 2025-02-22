from unittest import TestCase

from RequestProcessor.views import validate_json, validate_customer, \
    validate_ip, validate_ua


class Test(TestCase):
    def test_validate_missing_fields(self):
        data = '{"customerID":1,"tagID":2,"userID":"aaaaaaaa-bbbb-cccc-1111-222222222222","remoteIP":"123.234.56.78"}'
        json, isvalid = validate_json(data)
        self.assertFalse(isvalid)

    def test_validate_validjson(self):
        data = '{"customerID":1,"tagID":2,"userID":"aaaaaaaa-bbbb-cccc-1111-222222222222","remoteIP":"123.234.56.78","timestamp":1500000000}'
        json, isvalid = validate_json(data)
        self.assertTrue(isvalid)

    def test_validate_invalidjson(self):
        data = '"customerID": 12, "tagId'
        json, isvalid = validate_json(data)
        self.assertFalse(isvalid)

    def test_validate_customer(self):
        customerId = '1'
        customer, isvalid = validate_customer(customerId)
        self.assertTrue(isvalid)

    def test_inactive_customer(self):
        customerId = '3'
        customer, isvalid = validate_customer(customerId)
        self.assertFalse(isvalid)

    def test_invalid_customer(self):
        customerId = '3300'
        customer, isvalid = validate_customer(customerId)
        self.assertFalse(isvalid)

    def test_blacklisted_ip(self):
        self.assertFalse(validate_ip("123.234.56.78"))

    def test_nonblacklisted_ip(self):
         self.assertTrue(validate_ip("127.0.0.1"))

    def test_blacklisted_ua(self):
        self.assertFalse(validate_ua('Googlebot'))

    def test_nonblacklisted_ua(self):
        self.assertTrue(validate_ua('Localhost'))