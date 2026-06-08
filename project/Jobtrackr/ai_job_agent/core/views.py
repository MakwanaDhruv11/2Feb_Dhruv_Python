from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from jobs.models import Job
from resumes.models import Resume
from applications.models import SavedJob, Application
from matcher.models import JobMatch

class IndexView(TemplateView):
    """
    Renders dashboard if authenticated, else landing page.
    """
    template_name = 'core/index.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('core:dashboard')
        return super().get(request, *args, **kwargs)


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    User central workspace showing application tracking and metrics.
    """
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # 1. Compile metric counts
        context['resumes_count'] = Resume.objects.filter(user=user).count()
        context['jobs_count'] = Job.objects.filter(is_active=True).count()
        context['saved_count'] = SavedJob.objects.filter(user=user).count()
        context['applied_count'] = Application.objects.filter(user=user).count()
        
        # Calculate Average Match Score
        matches = JobMatch.objects.filter(user=user)
        if matches.exists():
            context['avg_match_score'] = round(sum(m.match_score for m in matches) / matches.count())
        else:
            context['avg_match_score'] = 0
            
        # 2. Recent items for tables
        context['recent_matches'] = matches[:5]
        context['recent_applications'] = Application.objects.filter(user=user)[:5]
        context['recent_resumes'] = Resume.objects.filter(user=user)[:3]
        
        return context


class MatchedJobsListView(LoginRequiredMixin, ListView):
    """
    Lists jobs matching user's uploaded resumes.
    """
    model = JobMatch
    template_name = 'core/matched_jobs.html'
    context_object_name = 'matches'
    paginate_by = 10

    def get_queryset(self):
        return JobMatch.objects.filter(user=self.request.user)


class SavedJobsListView(LoginRequiredMixin, ListView):
    """
    Lists jobs bookmarked by the user.
    """
    model = SavedJob
    template_name = 'core/saved_jobs.html'
    context_object_name = 'saved_jobs'
    paginate_by = 10

    def get_queryset(self):
        return SavedJob.objects.filter(user=self.request.user)


class AppliedJobsListView(LoginRequiredMixin, ListView):
    """
    Lists job applications tracked by the user.
    """
    model = Application
    template_name = 'core/applied_jobs.html'
    context_object_name = 'applications'
    paginate_by = 10

    def get_queryset(self):
        return Application.objects.filter(user=self.request.user)


class SettingsView(LoginRequiredMixin, TemplateView):
    """
    Mock configuration controls for the AI Agent settings.
    """
    template_name = 'core/settings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Seed settings context if needed
        return context


class SaveJobActionView(LoginRequiredMixin, View):
    """
    POST action to save/bookmark a job.
    """
    def post(self, request, pk, *args, **kwargs):
        job = get_object_or_404(Job, pk=pk)
        saved_job, created = SavedJob.objects.get_or_create(user=request.user, job=job)
        if created:
            messages.success(request, f"Saved '{job.title}' to your bookmark list.")
        else:
            messages.info(request, f"'{job.title}' was already in your bookmarks.")
        return redirect('jobs:job_detail', pk=pk)


class ApplyJobActionView(LoginRequiredMixin, View):
    """
    POST action to mark a job as applied.
    """
    def post(self, request, pk, *args, **kwargs):
        job = get_object_or_404(Job, pk=pk)
        application, created = Application.objects.get_or_create(
            user=request.user, 
            job=job,
            defaults={'status': 'applied'}
        )
        if created:
            messages.success(request, f"Added '{job.title}' to your application tracker.")
        else:
            messages.info(request, f"You are already tracking an application for '{job.title}'.")
        return redirect('jobs:job_detail', pk=pk)
