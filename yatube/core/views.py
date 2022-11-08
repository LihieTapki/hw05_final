from http import HTTPStatus

from django.http import HttpRequest
from django.shortcuts import HttpResponse, render


def page_not_found(request: HttpRequest, exception: Exception) -> HttpResponse:
    # не смог удалить лишний аргумент т.к. на аргс '*_' ругается pytest:
    # FAILED tests/test_homework.py::TestCustomErrorPages::test_custom_404 -
    # TypeError: page_not_found() got an unexpected keyword argument'exception'
    # а на кваргс **__ ругаются мои тесты:
    # ERRORS:?:(urls.E007)The custom handler404view'core.views.page_not_found'
    #  does not take the correct number of arguments (request, exception).
    return render(
        request,
        'core/404.html',
        {'path': request.path},
        status=HTTPStatus.NOT_FOUND,
    )


def csrf_failure(request: HttpRequest, reason: str = '') -> HttpResponse:
    return render(request, 'core/403csrf.html')


def server_error(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        'core/500.html',
        status=HTTPStatus.INTERNAL_SERVER_ERROR,
    )


def permission_denied(request: HttpRequest, *_) -> HttpResponse:
    return render(request, 'core/403.html', status=HTTPStatus.FORBIDDEN)
