from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=255, null=False)
    active = models.BooleanField(default=True)


class HourlyStats(models.Model):
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE)
    datetime = models.DateTimeField(null=False)
    request_count = models.BigIntegerField(null=False, default=0)
    invalid_count = models.BigIntegerField(null=False, default=0)

    class Meta:
        unique_together = ('customer_id', 'datetime')


## TODO : Add Blacklists