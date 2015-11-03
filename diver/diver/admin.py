__author__ = 'un'

from django.contrib import admin

#models
from diver.models import Image
from diver.models import Shop

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    pass






