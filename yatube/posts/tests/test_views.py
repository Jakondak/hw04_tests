from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title="Test",
            slug="test-slug"
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

    def test_main_page_shows_correct_context(self):
        response = self.authorized_client.get(reverse('index'))
        first_object = response.context['page'][0]
        post_text = first_object.text
        self.assertEqual(post_text, 'Тестовый текст')

    def test_group_page_shows_correct_context(self):
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': 'test-slug'}))
        first_object = response.context['page'][0]
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, 'Тестовый текст')

    def test_new_post_page_shows_correct_context(self):
        response = self.authorized_client.get(reverse('post_new'))
        form_fields = {
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_edit_post_page_shows_correct_context(self):
        response = self.authorized_client.get(f'/test_user/'
                                              f'{self.post.pk}/edit/')
        form_fields = {
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_new_post_group_page_dont_show_on_another_group_page(self):
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': 'test-slug'}))
        first_object = response.context['page'][0]
        group = first_object.group
        self.assertEqual(str(group), 'Test')

    def test_user_page_shows_correct_context(self):
        response = self.authorized_client.get(
            reverse('profile', kwargs={'username': 'test_user'}))
        first_object = response.context['page'][0]
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, 'Тестовый текст')

    def test_one_post_page_shows_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'post',
                kwargs={'username': 'test_user', 'post_id': f'{self.post.pk}'}
            )
        )
        first_object = response.context['post']
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, 'Тестовый текст')

    def test_pages_uses_correct_template(self):
        templates_page_names = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)


class PaginatorViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        for item in range(13):
            cls.post = Post.objects.create(
                text=f"Тестовый текст номер {item}",
            )

    def test_first_page_contains_ten_records(self):
        response = self.authorized_client.get(reverse('index'))
        self.assertEqual(len(response.context.get('page').object_list),
                         10)

    def test_second_page_contains_three_records(self):
        response = self.authorized_client.get(reverse('index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list),
                         3)
