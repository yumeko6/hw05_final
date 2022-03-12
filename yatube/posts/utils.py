from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404

from .models import Follow


def is_following(username):
    author = get_object_or_404(User, username=username).id
    following = Follow.objects.filter(author=author).exists()
    return following


def pagination(request, posts):
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
