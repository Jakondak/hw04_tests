from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post

User = get_user_model()


class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовое имя сообщества',
            slug='test-slug',
            description='Тестовое описание сообщества')
        cls.post = Post.objects.create(
            text="Тестовый текст",
            author=cls.user,
            group=cls.group,
        )
        cls.form = PostForm()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_task(self):
        tasks_count = Post.objects.count()

        form_data = {
            'text': 'Тестовый заголовок',
            'group': TaskCreateFormTests.group.id,
        }
        response = self.authorized_client.post(
            reverse('post_new'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), tasks_count + 1)

    def test_edit_post(self):
        form_data = {
            'text': 'Измененный тест',
            'group': TaskCreateFormTests.group.id,
        }
        response = self.authorized_client.post(
            f'/test_user/{self.post.pk}/edit/',
            data=form_data,
            follow=True,
        )
        self.assertEqual(
            str(response.context['post']), 'Измененный тест')
