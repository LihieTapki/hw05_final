from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import HttpResponse, get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from core.utils import paginate
from posts.forms import CommentForm, PostForm
from posts.models import Follow, Group, Post

User = get_user_model()


@cache_page(20, key_prefix='index_page')
def index(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        'posts/index.html',
        {
            'page_obj': paginate(
                request,
                Post.objects.select_related('group', 'author'),
                settings.QUANTITY_PER_PAGE,
            ),
        },
    )


def group_list(request: HttpRequest, slug: str) -> HttpResponse:
    group = get_object_or_404(Group, slug=slug)
    return render(
        request,
        'posts/group_list.html',
        {
            'group': group,
            'page_obj': paginate(
                request,
                group.posts.select_related('group', 'author'),
                settings.QUANTITY_PER_PAGE,
            ),
        },
    )


def profile(request: HttpRequest, username: str) -> HttpResponse:
    author = get_object_or_404(User, username=username)
    return render(
        request,
        'posts/profile.html',
        {
            'author': author,
            'page_obj': paginate(
                request,
                author.posts.select_related('group', 'author'),
                settings.QUANTITY_PER_PAGE,
            ),
            'following': request.user.is_authenticated
            and author.id
            in request.user.follower.values_list('author', flat=True),
        },
    )


def post_detail(request: HttpRequest, id: int) -> HttpResponse:
    post = get_object_or_404(Post, id=id)
    return render(
        request,
        'posts/post_detail.html',
        {
            'post': post,
            'form': CommentForm(),
            'comments': post.comments.select_related('post', 'author'),
            # коментарии отображаются под постом и формой по ТЗ
        },
    )


@login_required
def post_create(request: HttpRequest) -> HttpResponse:
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(
            request,
            'posts/create_post.html',
            {
                'form': form,
            },
        )

    form.instance.author = request.user
    form.save()
    return redirect('posts:profile', request.user.username)


def post_edit(request: HttpRequest, id: int) -> HttpResponse:
    post = Post.objects.get(pk=id)
    if request.user != post.author:
        return redirect('posts:post_detail', id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        post.save()
        return redirect('posts:post_detail', id)
    return render(
        request,
        'posts/create_post.html',
        {
            'form': form,
            'is_edit': True,
            'post': post,
        },
    )


@login_required
def add_comment(request: HttpRequest, id: int) -> HttpResponse:
    post = get_object_or_404(Post, id=id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        form.instance.author = request.user
        form.instance.post = post
        form.save()
    return redirect('posts:post_detail', id=id)


@login_required
def follow_index(request: HttpRequest) -> HttpResponse:
    following = request.user.follower.values_list('author', flat=True)
    posts = Post.objects.select_related('group', 'author').filter(
        author__in=following,
    )
    page_obj = paginate(request, posts, settings.QUANTITY_PER_PAGE)
    return render(
        request,
        'posts/follow.html',
        {
            'page_obj': page_obj,
        },
    )


@login_required
def profile_follow(request: HttpRequest, username: str) -> HttpResponse:
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', author.username)


@login_required
def profile_unfollow(request: HttpRequest, username: str) -> HttpResponse:
    follow = get_object_or_404(
        Follow,
        user=request.user,
        author__username=username,
    )
    follow.delete()
    return redirect('posts:index')
