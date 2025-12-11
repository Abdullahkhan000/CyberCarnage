from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    display_name = forms.CharField(required=False)
    bio = forms.CharField(required=False, widget=forms.Textarea)
    profile_pic = forms.URLField(required=False)

    class Meta:
        model = User
        fields = ("username", "email", "display_name", "bio", "profile_pic")


class LoginForm(AuthenticationForm):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
