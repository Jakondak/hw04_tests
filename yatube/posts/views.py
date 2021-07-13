from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User


def get_items_paginator(request, item, item_per_page):
    posts_list = item.posts.all()
    paginator = Paginator(posts_list, item_per_page)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return page


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.ELEMENTS_PAGINATOR)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "index.html", {"page": page})


def group_posts(request, slug):
    """Функция get_object_or_404 получает по заданным критериям
    объект из базы данных или возвращает сообщение об ошибке,
    если объект не найден.
    """
    group = get_object_or_404(Group, slug=slug)
    page = get_items_paginator(request, group, settings.ELEMENTS_PAGINATOR)
    return render(request, "group.html", {"group": group, "page": page})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    page = get_items_paginator(request, author, settings.ELEMENTS_PAGINATOR)
    return render(request, "profile.html", {"author": author, "page": page})


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author=author, pk=post_id)
    return render(request, "post.html", {"author": author, "post": post})


@login_required
def new_post(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data["text"]
            group = form.cleaned_data["group"]
            author = request.user
            post = Post(text=text, group=group, author=author)
            post.save()
            return redirect("index")
        return render(request, "new_post.html", {"form": form,
                                                 "switch": "new"})
    form = PostForm()
    return render(request, "new_post.html", {"form": form, "switch": "new"})


@login_required
def post_edit(request, username, post_id):
    if request.user.username != username:
        return redirect("post", username=username, post_id=post_id)
    item = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        form = PostForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect("post", username=username, post_id=post_id)
        return render(request, "new_post.html", {"form": form,
                                                 "switch": "edit"})
    form = PostForm(instance=item)
    return render(request, "new_post.html", {"form": form, "switch": "edit"})
