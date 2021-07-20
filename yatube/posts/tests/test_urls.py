from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()

group_link = 'group'
new_post_link = 'new'
edit_link = 'edit'
redirect_on_login_page_link = 'auth/login/?next='


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.user_watcher = User.objects.create_user(username='watcher')
        # Создадим запись в БД
        cls.group = Group.objects.create(
            title='Заголовок',
            slug='test-slug',
            description='description',
        )
        cls.post = Post.objects.create(
            text="Тестовый текст",
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_watcher_client = Client()
        self.authorized_watcher_client.force_login(self.user_watcher)

    def test_all_urls_exist_at_desired_location(self):
        type_client_urls_tuples = (
            (reverse('index'), self.guest_client),
            (f'/{group_link}/{self.group.slug}/', self.guest_client),
            (f'/{new_post_link}/', self.authorized_client),
            (f'/{self.user.username}/', self.guest_client),
            (f'/{self.user.username}/{self.post.pk}/', self.guest_client),
            (f'/{self.user.username}/{self.post.pk}/{edit_link}/',
                self.authorized_client),
            (reverse('about:author'), self.guest_client),
            (reverse('about:tech'), self.guest_client),
        )
        for tuple_item in type_client_urls_tuples:
            adress = tuple_item[0]
            client_type = tuple_item[1]
            with self.subTest(adress=adress):
                response = client_type.get(adress)
                self.assertEqual(response.status_code, 200)

    def test_all_urls_redirect_code(self):
        type_client_urls_tuples = (
            (f'/{new_post_link}/', self.guest_client),
            (f'/{self.user.username}/{self.post.pk}/{edit_link}/',
             self.guest_client),
            (f'/{self.user.username}/{self.post.pk}/{edit_link}/',
             self.authorized_watcher_client)
        )
        for tuple_item in type_client_urls_tuples:
            adress = tuple_item[0]
            client_type = tuple_item[1]
            with self.subTest(adress=adress):
                response = client_type.get(adress)
                self.assertEqual(response.status_code, 302)

    def test_urls_uses_correct_template(self):
        cache.clear()
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group.html': f'/{group_link}/{self.group.slug}/',
            'users/new_post.html': f'/{new_post_link}/',
        }
        for template, adress in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_post_edit_url_uses_correct_template(self):
        response = self.authorized_client.get(
            f'/{self.user.username}/{self.post.pk}/{edit_link}/'
        )
        self.assertTemplateUsed(response, 'users/new_post.html')

    def test_redirects_assert(self):
        type_client_urls_tuples = (
            (f'/{self.user.username}/{self.post.pk}/{edit_link}/',
             self.guest_client,
             f'/{redirect_on_login_page_link}/{self.user.username}/'
             f'{self.post.pk}/{edit_link}/'),
            (f'/{self.user.username}/{self.post.pk}/{edit_link}/',
             self.authorized_watcher_client,
             f'/{self.user.username}/{self.post.pk}/'),
        )
        for tuple_item in type_client_urls_tuples:
            adress = tuple_item[0]
            client_type = tuple_item[1]
            adress_redirect = tuple_item[2]
            with self.subTest(adress=adress):
                response = client_type.get(adress)
                self.assertRedirects(response, adress_redirect)
