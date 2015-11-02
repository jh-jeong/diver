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
