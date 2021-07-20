import shutil
import tempfile

from django.conf import settings
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
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
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

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

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
            f'/{self.user.username}/{self.post.pk}/edit/',
            data=form_data,
            follow=True,
        )
        self.assertEqual(
            str(response.context['post']), 'Измененный тест')
