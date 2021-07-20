import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title="Test",
            slug="test-slug"
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type="image/gif",
        )
        cls.image = uploaded
        cls.post = Post.objects.create(
            text="Тестовый текст",
            author=cls.user,
            group=cls.group,
            image=cls.image,
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

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
            reverse('group', args='test-slug'))
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
            reverse('group', args=['test-slug']))
        first_object = response.context['page'][0]
        group = first_object.group
        self.assertEqual(str(group), 'Test')

    def test_user_page_shows_correct_context(self):
        response = self.authorized_client.get(
            reverse('profile', args=['test_user']))
        first_object = response.context['page'][0]
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, 'Тестовый текст')

    def test_one_post_page_shows_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'post',
                args=['test_user', f'{self.post.pk}']
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

    def test_group_page_shows_correct_context(self):
        """Шаблон главной страницы сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('index'))
        first_object = response.context['page'][0]
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, str(self.post))

    def test_main_page_shows_pict(self):
        response = self.authorized_client.get(reverse('index'))
        first_object = response.context['page'][0]
        image = first_object.image
        self.assertEqual(image.name.split("/")[-1], self.image.name)

    def test_profile_page_shows_pict(self):
        response = self.authorized_client.get(
            reverse('profile', args=['test_user']))
        first_object = response.context['page'][0]
        image = first_object.image
        self.assertEqual(image.name.split("/")[-1], self.image.name)

    def test_group_page_shows_pict(self):
        response = self.authorized_client.get(
            reverse('group', args=['test-slug']))
        first_object = response.context['page'][0]
        image = first_object.image
        self.assertEqual(image.name.split("/")[-1], self.image.name)

    def test_one_post_page_shows_pict(self):
        response = self.authorized_client.get(
            reverse(
                'post',
                args=['test_user', f'{self.post.pk}']
            )
        )
        first_object = response.context['post']
        image = first_object.image
        self.assertEqual(image.name.split("/")[-1], self.image.name)


class PaginatorViewsTest(TestCase):
    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        num = 13
        Post.objects.bulk_create([
            Post(text=f"Тестовый текст номер {item}",
                 author=cls.user) for item in range(num)
        ])

    def test_first_page_contains_certain_amount_records(self):
        response_first_page = self.authorized_client.get(reverse('index'))
        response_second_page = self.authorized_client.get(
            reverse('index') + '?page=2'
        )
        self.assertEqual(
            len(response_first_page.context.get('page').object_list),
            10
        )
        self.assertEqual(
            len(response_second_page.context.get('page').object_list),
            3
        )
