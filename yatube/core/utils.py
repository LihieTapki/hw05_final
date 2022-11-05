from typing import Any

from django.core.paginator import Paginator
from django.http import HttpRequest


def paginate(request: HttpRequest, args: Any, quantity_per_page: int) -> Any:
    paginator = Paginator(args, quantity_per_page)
    return paginator.get_page(request.GET.get('page'))


def truncatechars(args: Any, chars_limit: int) -> Any:
    return args[:chars_limit] + '…' if len(args) > chars_limit else args
