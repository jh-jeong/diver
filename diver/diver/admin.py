__author__ = 'un'

from django.contrib import admin

#models
from diver.models import Image
from diver.models import Shop, Match
from diver.models import Item, Customer, Rating

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    pass

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    pass

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    pass

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    pass

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    pass

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    pass






