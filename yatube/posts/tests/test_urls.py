from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, Group

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Yusuf')
        cls.post = Post.objects.create(
            text='Текст поста',
            author=cls.user,
        )
        cls.group = Group.objects.create(
            title='Заголовок группы',
            slug='group-slag',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.template_names = [
            'posts/index.html',
            'posts/group_list.html',
            'posts/profile.html',
            'posts/post_detail.html',
            'posts/create_post.html',
            'posts/create_post.html',
        ]
        self.cases_list = [
            [reverse('posts:index'),
             self.guest_client, 200],
            [reverse('posts:group_list', args={self.group.slug}),
             self.guest_client, 200],
            [reverse('posts:profile', args={self.user.username}),
             self.guest_client, 200],
            [reverse('posts:post_detail', args={self.post.pk}),
             self.guest_client, 200],
            [reverse('posts:post_edit', args={self.post.pk}),
             self.authorized_client, 200],
            [reverse('posts:post_create'),
             self.authorized_client, 200],
            ['/unexisting_page/',
             self.guest_client, 404]
        ]

    def test_posts_urls_available_for_guest_client(self):
        """Страницы / , /group/<slug>/, /profile/username/,
         /posts/<post_id>/, /unexisting_page/
         доступны соответствующим пользователям."""
        for case in self.cases_list:
            with self.subTest(url=case[0]):
                response = case[1].get(case[0])
                self.assertEqual(response.status_code, case[2])

    def test_posts_urls_uses_correct_template(self):
        """Страницы используют соответствующие шаблоны."""
        for case, template in zip(self.cases_list, self.template_names):
            with self.subTest(url=case[0]):
                response = case[1].get(case[0])
                self.assertTemplateUsed(response, template)
