import json

from django.http import HttpResponse

from RequestProcessor.models import Customer

expected_fields = {"customerID", "tagID", "userID", "remoteIP", "timestamp"}


def process_valid(request):
    pass


def validate_json(data):
    # is valid json
    try:
        # is valid json
        json_data  = json.loads(data)
        # check for missing field
        if not expected_fields.issubset(json_data.keys()):
            # missing expected fields
            return False
        return True

    except Exception as e:
        return False


def validate_customer(customerId):
    # check if customer id in table is active
    return Customer.objects.filter(id=customerId, active=True).exists()


def process(request):
    if request.method == 'POST':
        if validate_json(request.body):
            if validate_customer(request.body['customerId']):
                process_valid(request)
                return HttpResponse("Valid Request")
            else:
                return HttpResponse("CustomerId invalid")
        else:
            return HttpResponse("Invalid Json in Request")
    else:
        return HttpResponse('Hello World!')
