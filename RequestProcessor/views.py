import json
from datetime import datetime
from json.decoder import JSONDecodeError

from django.core.exceptions import ObjectDoesNotExist
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.db.models import Sum

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
        # validate json
        request_data, valid = validate_json(request.body)
        if not valid:
            message += "Invalid JSON!\n"

        # derive the customer id and timestamp
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

        # add to stat table
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


def get_statistics(customerid, date):
    # Get data for the date
    stat_by_date = HourlyStats.objects.filter(date=date)

    # Get total requests on date
    total_reqs = stat_by_date.aggregate(total_req=
                                        Coalesce(Sum('request_count') +
                                                 Sum('invalid_count'), 0)
                                        )['total_req']

    # get all requests by the customer
    req_by_customer = stat_by_date.filter(customer_id=customerid).\
        order_by('hour')

    # sum valid and invalid requests by customer
    total_customer_reqs = req_by_customer.\
        aggregate(totalvalids=Coalesce(Sum('request_count'), 0),
                  totalinvalids=Coalesce(Sum('invalid_count'), 0)
                  )

    # prepare output
    stat = {
        'total_requests_on_date': total_reqs,
        'total_requests_by_customer': {
            'valid': total_customer_reqs['totalvalids'],
            'invalid': total_customer_reqs['totalinvalids']
        },
        'stat_by_hour': list(req_by_customer.values('hour', 'request_count',
                                                    'invalid_count'))
    }
    return stat


def get_date(date_data):
    try:
        date = datetime.strptime(date_data, "%d/%m/%Y")
        return date.date(), True
    except ValueError:
        return None, False


def stat(request):
    err_message = "Please send GET request to correct url " \
                  "e.g. /stat/?id=12&date=12/12/2021"
    message = ""
    if request.GET:
        try:
            customer_id = request.GET['id']
            date, isvalid = get_date(request.GET['date'])
            if not isvalid:
                raise ValueError

            message = json.dumps(get_statistics(customer_id, date))

        except (KeyError, ValueError):
            message = err_message
    else:
        message = err_message

    return HttpResponse(message)
