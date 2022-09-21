from django.db import models

# Create your models here.
class Transaction(models.Model):
    id = models.AutoField(primary_key=True)
    transaction_signature = models.CharField(max_length=200)
    transfer_identifier = models.IntegerField()
    account_number = models.CharField(max_length=20)
    user_name = models.CharField(max_length=20)
    transfer_amount = models.IntegerField()
    is_finish = models.BooleanField(default=False)