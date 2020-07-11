import json

from django.http import HttpResponse

expected_fields = set(["customerID", "tagID", "userID", "remoteIP", "timestamp"])


def process_valid(request):
    pass


def validate(data):
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


def process(request):
    if request.method == 'POST':
        if validate(request.body):
            process_valid(request)
            return HttpResponse("Valid Request")
        else:
            return HttpResponse("Invalid Request")
    else:
        return HttpResponse('Hello World!')
