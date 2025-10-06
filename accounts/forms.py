from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import NorthWindUser


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = NorthWindUser
        fields = ("email", "first_name", "last_name", "timezone")


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = NorthWindUser
        fields = ("email", "first_name", "last_name", "timezone")
