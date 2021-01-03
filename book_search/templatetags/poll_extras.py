from django import template
register = template.Library()


@register.filter
def get_obj(dictionary, key):
    obj = dictionary.get(key)
    return obj


@register.filter
def index(your_list, i):
    i = int(i)
    return your_list[i]

