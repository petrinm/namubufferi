from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models


class Account(models.Model):
    """
    https://docs.djangoproject.com/en/dev/topics/auth/customizing/#extending-the-existing-user-model
    """
    user = models.OneToOneField(User)
    balance = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    def make_payment(self, price):
        self.balance -= Decimal(price)
        self.save()

    def make_deposit(self, amount):
        self.balance += Decimal(amount)
        self.save()

    def __str__(self):
        return self.user.username


class Category(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=20, unique=True)
    category = models.ForeignKey(Category, related_name='products')
    price = models.FloatField(default=1)
    inventory = models.IntegerField(default=1)

    def make_sale(self):
        self.inventory += -1
        self.save()

    def cancel_sale(self):
        self.inventory += 1
        self.save()

    def __str__(self):
        return self.name


class Transaction(models.Model):
    amount = models.DecimalField(max_digits=5,
                                 decimal_places=2,
                                 default=0,
                                 )

    timestamp = models.DateTimeField(auto_now_add=True)
    timestamp.editable = False
    customer = models.ForeignKey(Account)
    product = models.ForeignKey(Product, null=True)
    canceled = models.BooleanField(default=False)

    def get_date_string(self):
        DATE_FORMAT = "%Y-%m-%d"
        TIME_FORMAT = "%H:%M:%S"

        if self.timestamp:
            return self.timestamp.strftime("%s %s" %
                                           (DATE_FORMAT, TIME_FORMAT))

    def cancel(self):
        if not self.canceled:
            self.customer.make_deposit(-self.amount)  # Note the minus sign
            self.canceled = True
            self.save()
            if self.product:
                self.product.cancel_sale()

    def __str__(self):
        return "%s, %s, %s" % (self.get_date_string(), self.customer.user.username, self.amount)

    class Meta:
        ordering = ["-timestamp"]
