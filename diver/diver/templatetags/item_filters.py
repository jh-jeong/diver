from django import template

from diver.models import Item, Color

register = template.Library()

@register.filter(name='category1')
def get_category1(category):
    return Item.get_category1(category)

@register.filter(name='hex_code')
def hex_code(color_id):
    return "#%02X%02X%02X" % Color.COLOR_VALUES[color_id][1]

@register.inclusion_tag('item_card_template.html')
def item_card(item, class_names):
    return {'item': item, 'class_names': class_names}

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

@register.inclusion_tag('match_item_template.html')
def match_item(cat1, num):
    items = Item.objects.filter(type=cat1)
    cat1 = Item.TYPES[cat1][1]

    return {'items': items, 'num': num, 'type': cat1}
