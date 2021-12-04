from django.db import models


class Site (models.Model):

    name = models.CharField(max_length=100, null=False, blank=False)
    url = models.URLField(max_length=100, null=False, blank=False)
    parser_name = models.CharField(max_length=30, null=False, blank=False)

    def __str__(self):
        return self.name


class Category(models.Model):

    name = models.CharField(max_length=100, null=False, blank=False)

    def __str__(self):
        return self.name


class Product (models.Model):

    name = models.CharField(max_length=100, null=False, blank=False)
    site = models.ForeignKey(Site, on_delete=models.RESTRICT, null=False, blank=False)
    url = models.URLField(max_length=250, null=False, blank=False)
    img = models.URLField(max_length=250, null=False, blank=False)
    category = models.ForeignKey(Category, on_delete=models.RESTRICT, null=False, blank=False)
    subcategory = models.CharField(max_length=100, null=True, blank=False)
    description = models.TextField(null=False, blank=True)
    article = models.CharField(max_length=100, null=False, blank=False)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(null=False, blank=False, default=False)

    @property
    def price(self):
        pass

    def __str__(self):
        return self.name


class Property (models.Model):

    name = models.CharField(max_length=100, null=False, blank=False)

    def __str__(self):
        return self.name


class ProductsProperties (models.Model):

    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False, blank=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, null=False, blank=False)
    value = models.CharField(max_length=100, null=False, blank=False)

    def __str__(self):
        return f'{self.property}: {self.value} for product {self.product}'


class Pricing (models.Model):

    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False, blank=False)
    date = models.DateTimeField(auto_now_add=True)
    price = models.FloatField()

    def __str__(self):
        return f'{self.product}: {self.price} at {self.date}'
