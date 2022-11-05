from typing import Any

from django import template
from django.http import HttpResponse

register = template.Library()


@register.filter
def addclass(field: Any, css: HttpResponse) -> HttpResponse:
    return field.as_widget(
        attrs={
            'class': css,
        },
    )
