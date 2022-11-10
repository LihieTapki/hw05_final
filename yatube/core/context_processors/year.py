from datetime import datetime

from django.http import HttpRequest
from django.shortcuts import HttpResponse


def year(request: HttpRequest) -> HttpResponse:
    return {
        'year': datetime.today().year,
    }
