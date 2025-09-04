from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import PlayerProfile

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    mc_username = forms.CharField(label="Pseudo Minecraft", max_length=32, required=False)

    class Meta:
        model = User
        fields = ("username", "email", "mc_username", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            profile = user.profile  # created by signal
            profile.mc_username = self.cleaned_data.get("mc_username")
            profile.save()
        return user
