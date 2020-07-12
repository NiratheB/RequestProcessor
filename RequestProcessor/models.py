from datetime import datetime

from django.db import models
from django.db.models import GenericIPAddressField, CharField
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
        # if invalid increment invalid count
        if not isvalid:
            stat.invalid_count = stat.invalid_count+1
        else:
            # increment req count
            stat.request_count = stat.request_count + 1

        return stat

    def __str__(self):
        return "Date: %s, Hour: %s, Customer: %s, Valid: %s, Invalid: %s" % (self.date,
                                                                            self.hour,
                                                                            self.customer_id,
                                                                            self.request_count,
                                                                            self.invalid_count)


    class Meta:
        unique_together = ('customer', 'date', 'hour')


class IPBlacklist(models.Model):
    ip = GenericIPAddressField(null=False, unique=True)


class UABlacklist(models.Model):
    ua = CharField(max_length=255, null=False, unique=True)
