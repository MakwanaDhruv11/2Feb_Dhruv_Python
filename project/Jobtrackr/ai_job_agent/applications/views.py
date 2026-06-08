from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Application, SavedJob
from jobs.models import Job

class ApplicationListView(LoginRequiredMixin, ListView):
    """
    Detailed tracker board of job applications.
    """
    model = Application
    template_name = 'applications/application_list.html'
    context_object_name = 'applications'

    def get_queryset(self):
        queryset = Application.objects.filter(user=self.request.user)
        status = self.request.GET.get('status', '').strip()
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', '')
        context['status_choices'] = Application.STATUS_CHOICES
        # Also grab saved jobs to render in a side tab on the same page
        context['saved_jobs'] = SavedJob.objects.filter(user=self.request.user)
        return context


class ApplicationUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    Allows editing notes and changing status.
    """
    model = Application
    fields = ['status', 'notes']
    template_name = 'applications/application_edit.html'
    success_url = reverse_lazy('applications:tracker_list')
    success_message = "Application tracked details updated."

    def get_queryset(self):
        return Application.objects.filter(user=self.request.user)


class ApplicationUpdateStatusView(LoginRequiredMixin, View):
    """
    Quick status transition trigger via POST.
    """
    def post(self, request, pk, *args, **kwargs):
        application = get_object_or_404(Application, pk=pk, user=request.user)
        new_status = request.POST.get('status')
        if new_status in dict(Application.STATUS_CHOICES):
            application.status = new_status
            application.save()
            messages.success(request, f"Application status updated to '{application.get_status_display()}'.")
        else:
            messages.error(request, "Invalid application status selected.")
        return redirect('applications:tracker_list')


class ApplicationDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """
    Stops tracking an application.
    """
    model = Application
    template_name = 'applications/application_confirm_delete.html'
    success_url = reverse_lazy('applications:tracker_list')
    success_message = "Stopped tracking application."

    def get_queryset(self):
        return Application.objects.filter(user=self.request.user)


class SavedJobDeleteView(LoginRequiredMixin, View):
    """
    Unbookmarks a saved job.
    """
    def post(self, request, pk, *args, **kwargs):
        saved_job = get_object_or_404(SavedJob, pk=pk, user=request.user)
        title = saved_job.job.title
        saved_job.delete()
        messages.success(request, f"Removed '{title}' from saved positions.")
        return redirect('applications:tracker_list')
