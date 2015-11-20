from django import template

from diver.models import Item

register = template.Library()

@register.filter(name='category1')
def get_category1(category):
    return Item.get_category1(category)

@register.inclusion_tag('hanger_item_template.html')
def hanger_item(item_ids, category1, slot_number):
    item = None
    if not item_ids == None:
        for item_id in item_ids:
            it = Item.objects.get(id=item_id)
            if category1.upper() == it.category1().upper():
                if slot_number == 0:
                    item = it
                    break
                else:
                    slot_number -= 1
    return {'item': item}
