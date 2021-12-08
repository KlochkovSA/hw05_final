from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post


def get_page(request, posts):
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    posts = Post.objects.select_related('author', 'group').all()
    paginator = get_page(request, posts)
    context = {
        'page_obj': paginator,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.post_group.select_related('author').all()
    paginator = get_page(request, posts)
    context = {
        'group': group,
        'page_obj': paginator
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(get_user_model(), username=username)
    posts = Post.objects.filter(author=author)
    paginator = get_page(request, posts)
    is_following = False

    if request.user.username:
        is_following = Follow.objects.filter(user=request.user,
                                             author=author
                                             ).exists()

    context = {
        'username': username,
        'page_obj': paginator,
        'author': author,
        'following': is_following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    details = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    comments = details.comments.all()
    context = {
        'form': form,
        'post_detail': details,
        'comments': comments
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user.username)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid() and post.author == request.user:
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'form': form,
        'is_edit': True
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, pk=post_id)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = []
    for following in request.user.follower.all():
        for post in following.author.posts.all():
            posts.append(post)

    paginator = get_page(request, posts)
    context = {'page_obj': paginator}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(get_user_model(), username=username)
    user = request.user
    is_followed: bool = Follow.objects.filter(user=user,
                                              author=author
                                              ).exists()
    if not is_followed and author != user:
        Follow.objects.create(user=user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(get_user_model(), username=username)
    user = request.user
    Follow.objects.get(user=user, author=author).delete()
    return redirect('posts:profile', username=username)
