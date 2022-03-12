from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template.defaultfilters import truncatewords

from .forms import PostForm, CommentForm
from .models import Post, Group, User, Follow, Comment
from .utils import pagination, is_following


def index(request):
    posts = Post.objects.select_related('author', 'group')
    page_obj = pagination(request, posts)
    context = {
        'page_obj': page_obj,
        'title': 'Последние обновления на сайте',
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group__slug=slug).select_related('group')
    page_obj = pagination(request, posts)
    context = {
        'group': group,
        'page_obj': page_obj,
        'title': f'Записи сообщества {group.title}',
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    post_author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(
        author__username=username).select_related('author')
    page_obj = pagination(request, posts)
    count = posts.count()
    following = is_following(post_author)
    context = {
        'username': post_author,
        'title': f'Профайл пользователя {post_author}',
        'page_obj': page_obj,
        'count': count,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all().filter(post_id=post_id)
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'title': f'Пост {truncatewords(post.text, 30)}',
        'form': form,
        'comments': comments,
        'post_author': post.author,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user)
    context = {
        'form': form,
        'title': 'Новый пост',
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    is_edit = True
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'title': 'Редактировать пост',
        'post': post,
        'is_edit': is_edit,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = pagination(request, posts)
    context = {
        'page_obj': page_obj,
        'title': 'Избранное'
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    user = get_object_or_404(User, username=request.user)
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=author).all()
    page_obj = pagination(request, posts)
    count = posts.count()
    if author != request.user:
        Follow.objects.get_or_create(
            user=user,
            author=author
        )
    following = is_following(username)
    context = {
        'username': author,
        'page_obj': page_obj,
        'count': count,
        'following': following,
        'title': f'Вы подписались на автора {author}'
    }
    return render(request, 'posts/profile.html', context)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    user = get_object_or_404(User, username=request.user)
    follow_user = Follow.objects.filter(
        user=user,
        author=author
    ).delete()
    following = is_following(username)
    context = {
        'username': author,
        'follow_user': follow_user,
        'following': following,
        'title': f'Вы отписались от автора {author}'
    }
    return render(request, 'posts/profile.html', context)
