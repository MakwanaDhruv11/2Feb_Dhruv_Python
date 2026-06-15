from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['username', 'age', 'is_public']

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age < 13:
            raise forms.ValidationError("User must be over 13 years old.")
        return age
