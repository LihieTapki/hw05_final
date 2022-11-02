from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import HttpResponse, get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from core.utils import paginate
from posts.forms import CommentForm, PostForm
from posts.models import Follow, Group, Post
from yatube.settings import QUANTITY_PER_PAGE

User = get_user_model()


@cache_page(20, key_prefix='index_page')
def index(request: HttpRequest) -> HttpResponse:
    posts = Post.objects.select_related('group', 'author')
    page_obj = paginate(request, posts, QUANTITY_PER_PAGE)
    return render(
        request,
        'posts/index.html',
        {
            'page_obj': page_obj,
        },
    )


def group_list(request: HttpRequest, slug: str) -> HttpResponse:
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('group', 'author')
    page_obj = paginate(request, posts, QUANTITY_PER_PAGE)
    return render(
        request,
        'posts/group_list.html',
        {
            'group': group,
            'page_obj': page_obj,
        },
    )


def profile(request: HttpRequest, username: str):
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('group', 'author')
    page_obj = paginate(request, posts, QUANTITY_PER_PAGE)
    if request.user.is_authenticated:
        follow_list = request.user.follower.values_list('author', flat=True)
        if author.id in follow_list:
            following = True
        else:
            following = False
    else:
        following = False
    return render(
        request,
        'posts/profile.html',
        {
            'author': author,
            'page_obj': page_obj,
            'following': following,
        },
    )


def post_detail(request, id: int) -> HttpResponse:
    post = get_object_or_404(Post, id=id)
    comments = post.comments.select_related('post', 'author')
    form = CommentForm(request.POST or None)
    return render(
        request,
        'posts/post_detail.html',
        {
            'post': post,
            'form': form,
            'comments': comments,
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

    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', post.author.username)


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
def add_comment(request, id):
    post = get_object_or_404(Post, id=id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', id=id)


@login_required
def follow_index(request):
    following = request.user.follower.values_list('author', flat=True)
    posts = Post.objects.filter(author__in=following)
    page_obj = paginate(request, posts, QUANTITY_PER_PAGE)
    return render(
        request,
        'posts/follow.html',
        {
            'page_obj': page_obj,
        },
    )


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    if author != user:
        Follow.objects.get_or_create(user=user, author=author)
        return redirect(
            'posts:profile',
            username=username,
        )
    return redirect('posts:profile', author.username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.get(user=request.user, author=author)
    follow.delete()
    return redirect('posts:index')
