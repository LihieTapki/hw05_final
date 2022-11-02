from django.core.paginator import Paginator


def paginate(request, args, quantity_per_page):
    paginator = Paginator(args, quantity_per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def truncatechars(args, chars_limit):
    return args[:chars_limit] + '…' if len(args) > chars_limit else args
