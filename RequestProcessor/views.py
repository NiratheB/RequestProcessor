import json
from datetime import datetime
from json.decoder import JSONDecodeError

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse

from RequestProcessor.models import Customer, HourlyStats, IPBlacklist, \
    UABlacklist

CUSTOMERID = "customerID"
TAGID = "tagID"
USERID = "userID"
REMOTEIP = "remoteIP"
TIMESTAMP = "timestamp"
expected_fields = {CUSTOMERID, TAGID, USERID, REMOTEIP, TIMESTAMP}


def process_valid(request):
    pass


def validate_json(data):
    # is valid json
    try:
        # is valid json
        json_data = json.loads(data)

        # check for missing field
        if not expected_fields.issubset(json_data.keys()):
            # missing expected fields
            return json_data, False
        return json_data, True

    except JSONDecodeError:
        return {}, False


def validate_customer(customerId):
    # check if customer id in table is active
    try:
        customer = Customer.objects.get(id=customerId)
        return customer, customer.active
    except ObjectDoesNotExist:
        return None, False


def validate_ip(remoteIP):
    return not IPBlacklist.objects.filter(ip=remoteIP).exists()


def validate_ua(useragent):
    return not UABlacklist.objects.filter(ua=useragent).exists()


def get_customer_id(data):
    if CUSTOMERID in data:
        return data[CUSTOMERID]
    else:
        return -1


def get_timestamp(data):
    try:
        value = datetime.fromtimestamp(float(data[TIMESTAMP]))
        return value, True
    except (KeyError, ValueError):
        # Error in timestamp
        return datetime.now(), False


def process(request):
    valid = True
    message = ""
    customer = None
    time = datetime.now()
    if request.method == 'POST':
        request_data, valid = validate_json(request.body)
        if not valid:
            message += "Invalid JSON!\n"
        if request_data:
            # validate customer
            customerid = get_customer_id(request_data)
            customer, isvalid = validate_customer(customerid)
            if not isvalid:
                message += "Invalid Customer ID!\n"
            valid = valid and isvalid

            # validate timestamp
            time, isvalid = get_timestamp(request_data)
            if not isvalid:
                message += "Invalid Timestamp!\n"
            valid = valid and isvalid

            if valid:
                # validate ip
                if not validate_ip(request_data[REMOTEIP]):
                    valid = False
                    message += "Blacklisted IP\n"
                elif not validate_ua(request_data[USERID]): # validate ua
                    valid = False
                    message += "Blacklisted User Agent\n"

        stat = HourlyStats.create(customer=customer,
                                      req_datetime=time,
                                      isvalid=valid)
        stat.save()

        if valid:
            process_valid(request)
            message = "Request is valid"
    else:
        message = "Please send POST request"

    return HttpResponse(message)
