from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Resume
from .forms import ResumeUploadForm
from .parser import extract_text_from_pdf, parse_resume_ai
import os

class ResumeUploadView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Resume
    form_class = ResumeUploadForm
    template_name = 'resumes/resume_upload.html'
    success_url = reverse_lazy('resumes:resume_list')
    success_message = "Resume uploaded and parsed successfully!"

    def form_valid(self, form):
        form.instance.user = self.request.user
        # Save first to write file on disk
        response = super().form_valid(form)
        
        # Now trigger text extraction and parsing
        resume = self.object
        file_path = resume.file.path
        
        try:
            # 1. Extract text from PDF
            raw_text = extract_text_from_pdf(file_path)
            resume.raw_text = raw_text
            
            # 2. Parse text into structured fields (Gemini or heuristic fallback)
            parsed_data = parse_resume_ai(raw_text)
            resume.parsed_data = parsed_data
            resume.is_parsed = True
            resume.save()
            
        except Exception as e:
            messages.error(self.request, f"Error parsing resume content: {str(e)}")
            
        return response


class ResumeListView(LoginRequiredMixin, ListView):
    model = Resume
    template_name = 'resumes/resume_list' # list templates usually default to app/model_list.html
    context_object_name = 'resumes'

    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)


class ResumeDetailView(LoginRequiredMixin, DetailView):
    model = Resume
    template_name = 'resumes/resume_detail.html'
    context_object_name = 'resume'

    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)


class ResumeDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Resume
    template_name = 'resumes/resume_confirm_delete.html'
    success_url = reverse_lazy('resumes:resume_list')
    success_message = "Resume deleted successfully."

    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)
