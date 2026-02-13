from django import template
from django.template.defaultfilters import stringfilter
import markdown as md

register = template.Library()

@register.filter()
@stringfilter
def markdown(value):
    return md.markdown(value, extensions=[
        'markdown.extensions.fenced_code',  # Helper for code blocks
        'markdown.extensions.codehilite',   # <--- SYNTAX HIGHLIGHTING (Colors)
        'markdown.extensions.tables',
        'markdown.extensions.nl2br',
        'markdown.extensions.sane_lists',   # <--- Fixes List Issues
        'pymdownx.tilde',                   # <--- Fixes ~~Strikethrough~~
    ], extension_configs={
        'markdown.extensions.codehilite': {
            'css_class': 'highlight',
            'use_pygments': True,
            'noclasses': False,             # Use CSS classes for coloring
        }
    })