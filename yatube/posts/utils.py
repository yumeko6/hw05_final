from django.core.paginator import Paginator

from .models import Follow


def is_following(author):
    following = Follow.objects.filter(author=author).exists()
    return following


def pagination(request, posts):
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
