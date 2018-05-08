from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.conf import settings
from django.core.mail import send_mail
import smtplib


# If you don't do this you cannot use Bootstrap CSS
class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username", max_length=30,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'username'}))
    password = forms.CharField(label="Password", max_length=30,
                               widget=forms.TextInput(attrs={'type': 'password', 'class': 'form-control', 'name': 'password'}))


class PasswordResetForm(UserCreationForm):
    #template_name = "registration/password_reset_form.html"
    email = forms.EmailField(label="Email", max_length=254,
                            widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'email'}))
    success_url = '/password_reset/done/'

    #send_mail('subject', 'body of the message', settings.EMAIL_HOST_USER, ['aparna.hariharasubramanian@latentview.com'])

    '''
    server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
    server.ehlo()
    server.starttls()
    server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
    msg = "Hello world from ATLAS mail"
    server.sendmail(settings.EMAIL_HOST_USER, "aparna.hariharasubramanian@latentview.com", msg)
    server.quit()
    '''


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )