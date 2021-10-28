# posts/views.py
from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator
from .models import Post, User, Group, Follow
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
# from django.views.decorators.cache import cache_page
from django.core.cache import cache


def index(request):
    template = 'posts/index.html'
    title = 'Последние обновления на сайте'
    paginator = Paginator(
        cache.get_or_set(
            'post_list',
            Post.objects.all(),
            20
        ), 10
    )
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'title': title,
               'page_obj': page_obj,
               }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    title = f'Записи сообщества {group.title}'
    post_list = group.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': title,
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    title = f'Профайл пользователя {author.get_full_name}'
    post_list = author.posts.all()
    posts_count = post_list.count()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    following = False
    if request.user.is_authenticated and Follow.objects.filter(
        user=request.user,
        author=author
    ).exists():
        following = True
    context = {
        'title': title,
        'author': author,
        'posts_count': posts_count,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    posts_count = post.author.posts.count()
    title = f'{post.text[:30]}'
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        'title': title,
        'post': post,
        'posts_count': posts_count,
        'form': form,
        'comments': comments
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/post_create.html'
    title = 'Новый пост'

    form = PostForm(request.POST or None, files=request.FILES or None)
    context = {
        'title': title,
        'form': form
    }
    if request.method == 'POST' and form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect('posts:profile', username=request.user.username)
    return render(request, template, context)


@login_required
def post_edit(request, post_id):

    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post.id)

    template = 'posts/post_create.html'
    title = 'Редактировать пост'
    is_edit = True

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    context = {
        'title': title,
        'form': form,
        'is_edit': is_edit,
    }
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post.id)
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = Post.objects.get(id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    template = 'posts/index.html'
    title = 'Новости'

    follows = request.user.follower.all()
    authors_list = []
    for follow in follows:
        authors_list.append(follow.author)

    post_list = Post.objects.filter(author__in=authors_list)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': title,
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    if request.user.username != username:
        Follow.objects.get_or_create(
            user=request.user,
            author=User.objects.get(username=username)
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
    try:
        Follow.objects.get(
            user=request.user,
            author=User.objects.get(username=username)
        ).delete()
    except Follow.DoesNotExist:
        pass
    return redirect('posts:profile', username=username)
