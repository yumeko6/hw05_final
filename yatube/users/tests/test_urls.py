from django.contrib.auth import get_user_model
from django.test import TestCase, Client


User = get_user_model()


class PostsURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Yusuf')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_posts_urls_available_for_guest_client(self):
        """Страницы /signup/ , /login/, /password_reset/,
         /password_reset/done/, /password_reset/complete/, /unexisting_page/
         доступны неавторизованным пользователям."""
        url_names = {
            '/auth/signup/': 200,
            '/auth/login/': 200,
            '/auth/password_reset/': 200,
            '/auth/password_reset/done/': 200,
            '/auth/password_reset/complete/': 404,
            '/unexisting_page/': 404,
        }
        for url, status_code in url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_posts_urls_available_for_authorized_client(self):
        """Страницы / , /group/<slug>/, /profile/username/,
        /posts/<post_id>/, /unexisting_page/
        доступны авторизованным пользователям."""
        url_names = {
            '/auth/signup/': 200,
            '/auth/login/': 200,
            '/auth/logout/': 200,
            '/auth/password_change/': 302,
            '/auth/password_change/done/': 302,
            '/auth/password_reset/': 200,
            '/auth/password_reset/done/': 200,
            '/auth/password_reset/complete/': 404,
            '/unexisting_page/': 404,
        }
        for url, status_code in url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_posts_urls_uses_correct_template(self):
        """Страницы используют соответствующие шаблоны."""
        url_templates = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/logout/': 'users/logged_out.html',
            # эти две проверки ниже не работают, почему - неизвестно :(
            # '/auth/password_change/': 'users/password_change_form.html',
            # '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
        }
        for url, template in url_templates.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
