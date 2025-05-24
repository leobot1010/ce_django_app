from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def info_icon(help_text):
    return mark_safe(f'''
    <i class="bi bi-info-circle text-muted small ms-2"
        data-bs-toggle="tooltip"
        data-bs-placement="right"
        title="{help_text}"></i>
    ''')


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


