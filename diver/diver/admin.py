__author__ = 'un'

from django.contrib import admin

#models
from diver.models import Image
from diver.models import Shop
from diver.models import Item

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    pass

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    pass

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    pass





