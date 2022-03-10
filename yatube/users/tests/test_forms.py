from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


User = get_user_model()


class SignUpFormTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_sign_up_form(self):
        """При заполнении формы reverse('users:signup')
         создаётся новый пользователь и доступна страница
          /profile/<username>."""
        form_data = {
            'first_name': 'Юсуф',
            'last_name': 'Питонов',
            'username': 'Yusuf',
            'email': 'yusuf@python.org',
            'password1': '!qaz@wsx',
            'password2': '!qaz@wsx',
        }
        response = self.client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:index'))
        response2 = self.client.get(f'/profile/{form_data["username"]}/')
        self.assertEqual(response2.status_code, 200)
