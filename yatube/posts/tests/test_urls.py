from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


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

    def test_home_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_group_url_exists_at_desired_location(self):
        response = self.guest_client.get('/group/test-slug/')
        self.assertEqual(response.status_code, 200)

    def test_new_post_url_exists_at_desired_location_authorized(self):
        response = self.authorized_client.get('/new/')
        self.assertEqual(response.status_code, 200)

    def test_new_post_url_exists_at_desired_location_not_authorized(self):
        response = self.guest_client.get('/new/')
        self.assertEqual(response.status_code, 302)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            'index.html': '/',
            'group.html': '/group/test-slug/',
            'new_post.html': '/new/',
        }
        for template, adress in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_profile_url_exists_at_desired_location(self):
        response = self.guest_client.get('/test_user/')
        self.assertEqual(response.status_code, 200)

    def test_one_post_url_exists_at_desired_location(self):
        response = self.guest_client.get(f'/test_user/{self.post.pk}/')
        self.assertEqual(response.status_code, 200)

    def test_post_edit_url_exists_at_desired_location_for_anonymous_user(self):
        response = self.guest_client.get(f'/test_user/{self.post.pk}/edit/')
        self.assertEqual(response.status_code, 302)

    def test_post_edit_url_exists_at_desired_location_for_author(self):
        response = self.authorized_client.get(
            f'/test_user/{self.post.pk}/edit/')
        self.assertEqual(response.status_code, 200)

    def test_post_edit_url_exists_at_desired_location_for_author(self):
        response = self.authorized_watcher_client.get(
            f'/test_user/{self.post.pk}/edit/')
        self.assertEqual(response.status_code, 302)

    def test_post_edit_url_uses_correct_template(self):
        response = self.authorized_client.get(
            f'/test_user/{self.post.pk}/edit/')
        self.assertTemplateUsed(response, 'new_post.html')

    def test_post_edit_url_redirect_anonymous_on_login_page(self):
        response = self.guest_client.get(f'/test_user/{self.post.pk}/edit/')
        self.assertRedirects(
            response, f'/auth/login/?next=/test_user/{self.post.pk}/edit/')

    def test_post_edit_url_redirect_login_user_on_same_page(self):
        response = self.authorized_watcher_client.get(
            f'/test_user/{self.post.pk}/edit/')
        self.assertRedirects( response, f'/test_user/{self.post.pk}/')

    def test_author_about_url_exists_at_desired_location(self):
        response = self.guest_client.get(reverse('about:author'))
        self.assertEqual(response.status_code, 200)

    def test_tech_about_url_exists_at_desired_location(self):
        response = self.guest_client.get(reverse('about:tech'))
        self.assertEqual(response.status_code, 200)
