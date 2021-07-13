from django.urls import path, reverse

from . import views

urlpatterns = [
    path("new/", views.new_post, name="post_new"),
    path(
        "<str:username>/<int:post_id>/edit/",
        views.post_edit,
        name="post_edit"),
    path("", views.index, name="index"),
    path("group/<slug:slug>/", views.group_posts, name="group"),
    path("<str:username>/", views.profile, name="profile"),
    path("<str:username>/<int:post_id>/", views.post_view, name="post"),
]


def test_group_page_shows_correct_context(self):
    """Шаблон главной страницы сформирован с правильным контекстом."""
    response = self.authorized_client.get(reverse('index'))
    first_object = response.context['page'][0]
    post_text_0 = first_object.text
    self.assertEqual(post_text_0, self.post)
