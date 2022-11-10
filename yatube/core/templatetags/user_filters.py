from django import forms, template
from django.http import HttpResponse

register = template.Library()


@register.filter
def addclass(field: forms, css) -> HttpResponse:
    return field.as_widget(
        attrs={
            'class': css,
        },
    )
