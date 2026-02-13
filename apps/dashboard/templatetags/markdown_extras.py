from django import template
from django.template.defaultfilters import stringfilter
import markdown as md

register = template.Library()

@register.filter()
@stringfilter
def markdown(value):
    return md.markdown(value, extensions=[
        'markdown.extensions.fenced_code',
        'markdown.extensions.codehilite',
        'markdown.extensions.tables',
        'markdown.extensions.nl2br',
        'markdown.extensions.sane_lists',
        'markdown.extensions.def_list',  # <--- ADDS DEFINITION LIST SUPPORT
        'pymdownx.tilde',
        'pymdownx.tasklist',
    ], extension_configs={
        'markdown.extensions.codehilite': {
            'css_class': 'highlight',
            'use_pygments': True,
            'noclasses': False,
        },
        'pymdownx.tasklist': {
            'custom_checkbox': True,
            'clickable_checkbox': False,
        }
    })