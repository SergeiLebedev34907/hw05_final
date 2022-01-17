# posts/views.py
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def pagin(request, database_query, posts_on_page=settings.POSTS_ON_PAGE):
    paginator = Paginator(database_query, posts_on_page)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    template = "posts/index.html"
    title = "Последние обновления на сайте"

    database_query = cache.get_or_set(
        "index_post_list",
        Post.objects.select_related("author", "group").all(),
        20,
    )
    page_obj = pagin(request, database_query)

    context = {
        "title": title,
        "page_obj": page_obj,
    }
    return render(request, template, context)


def groups(request):
    template = "posts/groups.html"
    title = "Группы"
    page_obj = pagin(request, Group.objects.all())

    context = {
        "title": title,
        "page_obj": page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)

    template = "posts/group_list.html"
    title = f"Записи сообщества {group.title}"
    page_obj = pagin(request, group.posts.select_related("author").all())

    context = {
        "title": title,
        "group": group,
        "page_obj": page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    posts_count = post_list.count()

    template = "posts/profile.html"
    title = f"Профайл пользователя {author.get_full_name}"
    page_obj = pagin(request, author.posts.select_related("group").all())

    following = None
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=author
        ).exists()

    context = {
        "title": title,
        "author": author,
        "page_obj": page_obj,
        "posts_count": posts_count,
        "following": following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post.objects.select_related(), pk=post_id)

    template = "posts/post_detail.html"
    title = f"{post.text[:30]}"

    posts_count = post.author.posts.count()
    form = CommentForm(request.POST or None)
    comments = post.comments.all()

    context = {
        "title": title,
        "post": post,
        "posts_count": posts_count,
        "form": form,
        "comments": comments,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = "posts/post_create.html"
    title = "Новый пост"

    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == "POST" and form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect("posts:profile", request.user.username)
    context = {"title": title, "form": form}
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect("posts:post_detail", post.id)

    template = "posts/post_create.html"
    title = "Редактировать пост"
    is_edit = True

    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("posts:post_detail", post.id)
    context = {
        "title": title,
        "form": form,
        "is_edit": is_edit,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect("posts:post_detail", post_id)


@login_required
def follow_index(request):
    template = "posts/index.html"
    title = "Новости"
    page_obj = pagin(
        request, Post.objects.filter(author__following__user=request.user)
    )
    context = {
        "title": title,
        "page_obj": page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    if request.user.username != username:
        Follow.objects.get_or_create(
            user=request.user,
            author=get_object_or_404(User, username=username),
        )
    return redirect("posts:profile", username)


@login_required
def profile_unfollow(request, username):
    Follow.objects.filter(
        user=request.user, author=get_object_or_404(User, username=username)
    ).delete()
    return redirect("posts:profile", username)
