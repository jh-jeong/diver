from django.db import models

class Customer(models.Model):
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=128)
    height_cm = models.IntegerField()
    weight_km = models.IntegerField()
    shirt_size = models.IntegerField()
    pants_size = models.IntegerField()
    cap_size = models.IntegerField()
    # body shape

    def like(item):
        pass

    def dislike(item):
        pass

    def modify_score(recommendation):
        pass

class Shop(models.Model):
    name = models.CharField(max_length=30)
    url = models.URLField()
    items = models.ManyToManyField(Item)
    matches = models.ManyToManyField(Match)

class Match(models.Model):
    items = models.ManyToManyField(Item)
    images = models.ManyToManyField(Image)

class Item(models.Model):
    name = models.CharField(max_length=30)

    # this is an example
    category = (
        (0,"shirt"),
        (1,"pants"),
        (2,"skirt"),
    )
    size = models.IntegerField()
    price = models.IntegerField()
    images = models.ManyToManyField(Image)
    purchase_url = models.URLField()
    shop = models.ForeignKey(Shop)

class Image(models.Model):
    image = models.ImageField(null=True)
