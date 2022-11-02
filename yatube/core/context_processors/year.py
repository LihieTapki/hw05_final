from datetime import datetime

from django.http import HttpRequest
from django.shortcuts import HttpResponse


def year(request: HttpRequest) -> HttpResponse:
    year = datetime.today().year
    return {
        'year': year,
    }
