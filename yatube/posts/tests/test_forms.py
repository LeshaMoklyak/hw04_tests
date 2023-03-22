import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Post, Group


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=PostCreateFormTests.author,
            text='Тестовый пост',
            group=cls.group
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guess_client = Client()
        self.user = User.objects.create(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_create_post(self):
        tasks_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый заголовок2',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse('posts:profile', kwargs={
            'username': self.user.username,
        }))
        self.assertEqual(Post.objects.count(), tasks_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый заголовок2',
                group=self.group.id,
            ).exists()
        )

    def test_edit_post(self):
        form_data = {
            'text': 'Редактирование поста',
            'group': self.group.id,
        }
        response = self.author_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
        )
        self.assertRedirects(response, reverse('posts:post_detail', kwargs={
            'post_id': self.post.id}))
        self.assertTrue(Post.objects.filter(
            text='Редактирование поста',
            group=self.group.id,
        ).exists()
        )
