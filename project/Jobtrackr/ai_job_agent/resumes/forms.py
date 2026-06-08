from django import forms
from .models import Resume

class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ('file',)
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'form-control bg-dark border-secondary text-white',
                'accept': '.pdf'
            })
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            extension = file.name.split('.')[-1].lower()
            if extension != 'pdf':
                raise forms.ValidationError("Only PDF resumes are supported.")
        return file
