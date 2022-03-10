import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django import forms

from ..models import Post, Group, Follow

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Yusuf')
        cls.group = Group.objects.create(
            title='Заголовок группы',
            slug='group-slag',
        )
        cls.my_image = (
             b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='my_image.png',
            content=cls.my_image,
            content_type='image/png'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Все будет хорошо!',
            image=cls.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        template_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user.username}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}):
                'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}):
                'posts/create_post.html',
        }
        for reverse_name, template in template_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_some_pages_show_correct_context(self):
        """Шаблоны posts/index.html, posts/group_list.html,
         posts/profile.html ожидают в контексте
         списки отфильтрованных постов с загруженной картинкой."""
        page_list = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username}),
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}),
        ]
        for page in page_list:
            with self.subTest(page_list=page_list):
                response = self.guest_client.get(page)
                if page == page_list[3]:
                    page_post = response.context['post']
                    self.assertTrue(page_post)
                    image_obj = response.context['post']
                    self.assertEqual(image_obj.image, self.post.image)
                else:
                    page_post = list(response.context['page_obj'])
                    self.assertTrue(page_post)
                    image_obj = response.context['page_obj'][0]
                    self.assertEqual(image_obj.image, self.post.image)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Заголовок группы',
            slug='group-slag',
        )
        cls.user = User.objects.create_user(username='Yusuf')
        for i in range(1, 13):
            cls.post = Post.objects.create(author=cls.user, group=cls.group)

    def setUp(self):
        self.guest_client = Client()

    def test_first_and_second_pages_contains_ten_and_two_records(self):
        """На первой странице 10 постов, на второй 2 поста."""
        reverse_names = (reverse('posts:index'),
                         reverse('posts:group_list',
                                 kwargs={'slug': self.group.slug}),
                         reverse('posts:profile',
                                 kwargs={'username': self.user.username})
                         )

        for reverse_name in reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), 10)

        for reverse_name in reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 2)


class PostTextTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Yusuf')
        cls.group = Group.objects.create(
            title='Заголовок группы',
            slug='group-slag',
        )
        cls.another_group = Group.objects.create(
            title='Заголовок другой группы',
            slug='group-slag-another',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Текст первого поста',
        )
        cls.post2 = Post.objects.create(
            author=cls.user,
            group=cls.another_group,
            text='Новый текст второго поста другой группы',
        )

    def setUp(self):
        self.guest_client = Client()

    def test_created_post_on_some_page(self):
        """Созданный пост появился на страницах
         /index/, /group/<slug:slug>/, /profile/<username>/
         и не отображается в другой группе."""
        reverse_names = (reverse('posts:index'),
                         reverse('posts:group_list',
                                 kwargs={'slug': self.group.slug}),
                         reverse('posts:profile',
                                 kwargs={'username': self.user.username})
                         )
        response = self.guest_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': self.another_group.slug}))
        response_object = len(response.context['page_obj'])
        self.assertEqual(response_object, 1)
        for reverse_name in reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                first_object = response.context['page_obj'][0]
                self.assertIn(first_object, list(response.context['page_obj']))


class ContextTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Yusuf')
        cls.group = Group.objects.create(
            title='Заголовок группы',
            slug='group-slag',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Текст созданного поста',
        )
        cls.post2 = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Текст созданного поста с группой',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_some_pages_expects_filtered_post_list(self):
        """На страницах index, group_list, profile
        выведен список отфильтрованных постов."""
        reverse_names = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username}),
        )
        for reverse_name in reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), 2)

    def test_post_detail_page_expects_filtered_by_id_post(self):
        """На странице post_detail выводится пост, отфильтрованный по id."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}))
        self.assertEqual(response.context.get('post').text, self.post.text)
        self.assertEqual(response.context.get('post').author, self.post.author)
        self.assertEqual(response.context.get('post').group, self.post.group)

    def test_create_post_page_expects_edit_form(self):
        """Выводится форма редактирования поста, отфильтрованного по id."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_create_post_page_expects_create_form(self):
        """Выводится форма создания поста."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_authorized_client_can_comment(self):
        """Только авторизованный пользователь может оставлять комментарии."""
        response = self.guest_client.get(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}))
        self.assertEqual(
            response.url,
            f'{reverse("users:login")}'
            f'?next='
            f'{reverse("posts:add_comment", kwargs={"post_id": self.post.pk})}'
        )


class CacheTest(TestCase):
    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.user = User.objects.create_user(username='123')
        self.post = Post.objects.create(
            author=self.user,
            text='произвольный текст'
        )

    def test_cache_index_page(self):
        key = make_template_fragment_key('index_page')
        response1 = self.guest_client.get(reverse('posts:index'))
        cache1 = cache.get(key)
        my_post = Post.objects.get(id=self.post.pk)
        my_post.delete()
        response2 = self.guest_client.get(reverse('posts:index'))
        cache2 = cache.get(key)
        self.assertEqual(cache1, cache2)
        cache.clear()
        response3 = self.guest_client.get(reverse('posts:index'))
        cache3 = cache.get(key)
        self.assertNotEqual(cache2, cache3)


class FollowTest(TestCase):
    def setUp(self):
        self.follower = User.objects.create_user(username='Follower')
        self.author = User.objects.create_user(username='Yusuf')
        self.guest = User.objects.create_user(username='Guest')
        self.post = Post.objects.create(
            author=self.author,
            text='Текст поста для подписчика'
        )
        self.guest_client = Client()
        self.follower_client = Client()
        self.unauthorized_client = Client()
        self.guest_client.force_login(self.guest)
        self.follower_client.force_login(self.follower)

    def test_follow_unfollow_via_button(self):
        """Авторизованный пользователь может подписаться, отписаться,
        в базе данных появляется запись, в избранном появляется пост автора,
        другой пользователь не видит чужой подписки, неавторизованный
        не может подписаться."""
        follow_count = Follow.objects.count()
        following = self.follower_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.author.username})
        )
        follow_object = Follow.objects.get(user=self.follower.pk,
                                           author=self.author.pk)
        self.assertIn(follow_object, Follow.objects.all())
        follow_index = self.follower_client.get(
            reverse('posts:follow_index')
        )
        follow_index_guest = self.guest_client.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(len(follow_index.context['page_obj']),
                         follow_count + 1)
        self.assertEqual(len(follow_index_guest.context['page_obj']),
                         follow_count)

        unfollowing = self.follower_client.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.author.username})
        )
        self.assertNotIn(follow_object, Follow.objects.all())
        follow_index = self.follower_client.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(len(follow_index.context['page_obj']),
                         follow_count)
        response = self.unauthorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.author.username}
            )
        )
        self.assertEqual(
            response.url,
            f'{reverse("users:login")}'
            f'?next='
            f'{reverse("posts:profile_follow", args=[self.author.username])}'
        )
