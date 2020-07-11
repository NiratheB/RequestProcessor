from datetime import datetime

from django.db import models
from django.utils.timezone import now

class Customer(models.Model):
    name = models.CharField(max_length=255, null=False)
    active = models.BooleanField(default=True)


class HourlyStats(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    date = models.DateField(null=False, default=now().date())
    hour = models.IntegerField(null= False, default=now().hour)
    request_count = models.BigIntegerField(null=False, default=0)
    invalid_count = models.BigIntegerField(null=False, default=0)

    @classmethod
    def create(cls, customer, req_datetime: datetime, isvalid):
        date = req_datetime.date()
        hour = req_datetime.hour
        # check if exists
        stat, existing = cls.objects.get_or_create(customer=customer,
                                         date=date,
                                         hour=hour)
        # increment req count
        stat.request_count = stat.request_count+1
        # if invalid increment invalid count
        if not isvalid:
            stat.invalid_count = stat.invalid_count+1

        return stat


    class Meta:
        unique_together = ('customer', 'date', 'hour')


## TODO : Add Blacklists