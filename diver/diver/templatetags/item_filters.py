from django import template

from diver.models import Item

register = template.Library()

@register.filter(name='category1')
def get_category1(category):
    for category1 in Item.CATEGORIES:
        for category2 in category1[1]:
            if category.upper() == category2[0].upper():
                return category1[0]
