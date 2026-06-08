from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import CoverLetter
from .generator import generate_cover_letter_ai, generate_assisted_apply_data
from resumes.models import Resume
from jobs.models import Job

class CoverLetterGenerateView(LoginRequiredMixin, View):
    """
    Renders cover letter generator configuration page and processes AI generation POST requests.
    """
    def get(self, request, *args, **kwargs):
        job_id = request.GET.get('job_id')
        job = get_object_or_404(Job, pk=job_id)
        resumes = Resume.objects.filter(user=request.user)
        
        if not resumes.exists():
            messages.warning(request, "Please upload a baseline resume first before generating a cover letter.")
            return redirect('resumes:resume_upload')
            
        return render(request, 'automation/cover_letter_form.html', {
            'job': job,
            'resumes': resumes
        })

    def post(self, request, *args, **kwargs):
        job_id = request.POST.get('job_id')
        resume_id = request.POST.get('resume_id')
        
        job = get_object_or_404(Job, pk=job_id)
        resume = get_object_or_404(Resume, pk=resume_id, user=request.user)
        
        try:
            content = generate_cover_letter_ai(resume, job)
            letter = CoverLetter.objects.create(
                user=request.user,
                resume=resume,
                job=job,
                content=content
            )
            messages.success(request, f"AI Cover Letter for {job.company} generated successfully!")
            return redirect('automation:cover_letter_detail', pk=letter.pk)
        except Exception as e:
            messages.error(request, f"Failed to generate cover letter: {str(e)}")
            return redirect('jobs:job_detail', pk=job.pk)


class CoverLetterListView(LoginRequiredMixin, ListView):
    model = CoverLetter
    template_name = 'automation/cover_letter_list.html'
    context_object_name = 'cover_letters'

    def get_queryset(self):
        return CoverLetter.objects.filter(user=self.request.user)


class CoverLetterDetailView(LoginRequiredMixin, DetailView):
    model = CoverLetter
    template_name = 'automation/cover_letter_detail.html'
    context_object_name = 'letter'

    def get_queryset(self):
        return CoverLetter.objects.filter(user=self.request.user)


class CoverLetterDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = CoverLetter
    template_name = 'automation/cover_letter_confirm_delete.html'
    success_url = reverse_lazy('automation:cover_letter_list')
    success_message = "Cover letter deleted successfully."

    def get_queryset(self):
        return CoverLetter.objects.filter(user=self.request.user)


class AssistedApplyView(LoginRequiredMixin, View):
    """
    Assembles a dual-pane copypasta dashboard helper for job applications.
    """
    def get(self, request, *args, **kwargs):
        job_id = request.GET.get('job_id')
        job = get_object_or_404(Job, pk=job_id)
        resumes = Resume.objects.filter(user=request.user)
        
        if not resumes.exists():
            messages.warning(request, "Please upload a baseline resume first to use Assisted Apply.")
            return redirect('resumes:resume_upload')
            
        # Select active resume
        resume_id = request.GET.get('resume_id')
        if resume_id:
            active_resume = get_object_or_404(Resume, pk=resume_id, user=request.user)
        else:
            active_resume = resumes.first()

        # Fetch custom screening question answers cheat sheet
        apply_data = generate_assisted_apply_data(active_resume, job)

        return render(request, 'automation/assisted_apply.html', {
            'job': job,
            'resumes': resumes,
            'active_resume': active_resume,
            'apply_data': apply_data
        })
