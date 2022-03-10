from django.views.generic import CreateView, FormView
from django.urls import reverse_lazy
from .forms import CreationForm, PasswordForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class PasswordChange(FormView):
    form_class = PasswordForm
    success_url = reverse_lazy('users:password_change_done')
    template_name = 'users/password_change_form.html'


class PasswordReset(FormView):
    form_class = PasswordForm
    success_url = reverse_lazy('users:password_reset_done')
    template_name = 'users/password_reset_form.html'


class PasswordResetConfirm(FormView):
    form_class = PasswordForm
    success_url = reverse_lazy('users:password_reset_complete')
    template_name = 'users/password_reset_confirm.html'
