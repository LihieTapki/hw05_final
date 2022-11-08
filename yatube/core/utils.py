from django.conf import settings
from django.core.paginator import Paginator
from django.http import HttpRequest
from django.db.models import QuerySet


def paginate(
    request: HttpRequest,
    queryset: QuerySet,
    pagesize: int = settings.PAGE_SIZE,
) -> QuerySet:
    return Paginator(queryset, pagesize).get_page(request.GET.get('page'))


def truncatechars(chars: str, chars_limit: int = settings.NUMCATECHARS) -> str:
    return chars[:chars_limit] + '…' if len(chars) > chars_limit else chars
