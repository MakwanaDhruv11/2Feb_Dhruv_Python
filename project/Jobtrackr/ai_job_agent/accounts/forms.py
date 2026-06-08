from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Required. Input a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number', 'bio')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Tell us about your career goals...'}),
            'phone_number': forms.TextInput(attrs={'placeholder': '+1234567890'}),
        }

    def save(self, commit=True):
        user = super().save(commit=commit)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number', 'bio')


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'bio')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control bg-dark border-secondary text-white'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control bg-dark border-secondary text-white'}),
            'email': forms.EmailInput(attrs={'class': 'form-control bg-dark border-secondary text-white'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control bg-dark border-secondary text-white'}),
            'bio': forms.Textarea(attrs={'class': 'form-control bg-dark border-secondary text-white', 'rows': 4}),
        }
