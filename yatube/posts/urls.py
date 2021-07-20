from django.conf.urls import handler404, handler500  # noqa
from django.urls import path, reverse

from . import views

handler404 = "posts.views.page_not_found"  # noqa
handler500 = "posts.views.server_error"  # noqa

urlpatterns = [
    path("new/", views.new_post, name="post_new"),
    path(
        "<str:username>/<int:post_id>/edit/",
        views.post_edit,
        name="post_edit"),
    path("400/", views.page_not_found, name="not_found"),
    path("500/", views.server_error, name="server_error"),

    path("", views.index, name="index"),
    path("group/<slug:slug>/", views.group_posts, name="group"),
    path("<str:username>/", views.profile, name="profile"),
    path("<str:username>/<int:post_id>/", views.post_view, name="post"),
    path(
        "<str:username>/<int:post_id>/comment/",
        views.add_comment,
        name="add_comment"
    ),
]
