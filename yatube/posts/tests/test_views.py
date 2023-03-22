from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from ..models import Post, Group
from django import forms
import time


User = get_user_model()


class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.group2 = Group.objects.create(
            title='Тестовый заголовок 2',
            slug='test-slug2',
            description='Тестовое описание 2'
        )
        for item in range(0, 15):
            time.sleep(0.1)
            cls.post = Post.objects.create(
                author=PostViewsTest.author,
                text=f'Тестовый пост номер:{item}',
                group=cls.group
            )

    def setUp(self):
        self.user = User.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_pages_auth_user_correct_template(self):
        templates_pages_names = {
            'posts:index': reverse('posts:index'),
            'posts/create_post.html': reverse('posts:post_create'),
            'posts/group_list.html': (
                reverse('posts:post_list', kwargs={'slug': 'test-slug'})
            ),
            'posts/profile.html': (
                reverse('posts:profile', kwargs={'username': 'auth'})
            )
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_auth_user_correct_template(self):
        templates_pages_names = {
            'posts/create_post.html': (
                reverse('posts:post_edit', kwargs={'post_id': '1'})
            ),
            'posts/post_detail.html': (
                reverse('posts:post_detail', kwargs={'post_id': '1'})
            )
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, PostViewsTest.post.text)
        self.assertEqual(first_object.author, PostViewsTest.post.author)
        self.assertEqual(first_object.group, PostViewsTest.group)

        self.assertEqual(len(response.context['page_obj']), 10)
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 5)

    def test_group_list_show_correct_context(self):
        response = self.authorized_client.\
            get(reverse('posts:post_list', kwargs={
                'slug': PostViewsTest.group.slug
            }))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        group_obj = response.context['group']
        self.assertEqual(group_obj.title, PostViewsTest.group.title)
        self.assertEqual(
            group_obj.description, PostViewsTest.group.description
        )
        page_obj = response.context['page_obj'][0]
        self.assertEqual(page_obj.author, PostViewsTest.author)
        self.assertEqual(page_obj.text, PostViewsTest.post.text)

        self.assertEqual(len(response.context['page_obj']), 10)
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 5)

    def test_profile_show_correct_context(self):
        response = self.authorized_client.\
            get(reverse('posts:profile', kwargs={'username': 'auth'}))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        profile_obj = response.context['author']
        self.assertEqual(
            profile_obj.username, PostViewsTest.author.username
        )

        page_obj = response.context['page_obj'][0]
        self.assertEqual(page_obj.text, PostViewsTest.post.text)
        self.assertEqual(page_obj.group, PostViewsTest.group)

        self.assertEqual(len(response.context['page_obj']), 10)
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 5)

    def test_post_detail_show_correct_context(self):
        response = self.authorized_client.\
            get(reverse(
                'posts:post_detail', kwargs={'post_id': PostViewsTest.post.id}
            ))
        page_obj = response.context['post']
        self.assertEqual(page_obj.text, PostViewsTest.post.text)
        self.assertEqual(page_obj.group, PostViewsTest.group)
        self.assertEqual(page_obj.author, PostViewsTest.author)

    def test_create_post_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            # При создании формы поля модели типа TextField
            # преобразуются в CharField с виджетом forms.Textarea
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    def test_edit_post_show_correct_context(self):
        response = self.author_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': PostViewsTest.post.id})
        )
        form_field = response.context.get('form').instance.id
        self.assertEqual(form_field, PostViewsTest.post.id)

    def test_create_post_with_one_group(self):
        responce = self.authorized_client.get(reverse(
            'posts:post_list', kwargs={'slug': 'test-slug2'}))
        page_obj = responce.context['page_obj']
        self.assertEqual(len(page_obj), 0)
