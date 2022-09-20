from django.db import models

# Create your models here.
class AssetGroup(models.Model):
    id = models.AutoField(primary_key=True)
    asset_group_name = models.CharField(max_length=20)


class StockFirm(models.Model):
    id = models.AutoField(primary_key=True)
    stock_firm_name = models.CharField(max_length=20)


class Account(models.Model):
    id = models.AutoField(primary_key=True)
    account_holder = models.CharField(max_length=20)
    stock_firm_id = models.ForeignKey(StockFirm, on_delete=models.SET_NULL, null=True)
    account_number = models.IntegerField(unique=True)
    account_name = models.CharField(max_length=20)
    investment_principal = models.IntegerField()


class Stock(models.Model):
    id = models.AutoField(primary_key=True)
    stock_name = models.CharField(max_length=20)
    isin = models.CharField(max_length=20, unique=True)
    asset_group_id = models.ForeignKey(AssetGroup, on_delete=models.SET_NULL, null=True)


class StockSheld(models.Model):
    id = models.AutoField(primary_key=True)
    account_id = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    stock_id = models.ForeignKey(Stock, on_delete=models.SET_NULL, null=True)
    current_price = models.IntegerField()
    amount = models.IntegerField()
