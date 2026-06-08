from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from .models import Job
from .services import JobFetcherService

class JobListView(LoginRequiredMixin, ListView):
    model = Job
    template_name = 'jobs/job_list.html'
    context_object_name = 'jobs'
    paginate_by = 12

    def get_queryset(self):
        queryset = Job.objects.filter(is_active=True)
        
        # 1. Search Query Filter
        q = self.request.GET.get('q', '').strip()
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(company__icontains=q) |
                Q(description__icontains=q) |
                Q(tags__icontains=q) # JSONField contains
            )

        # 2. Source Filter
        source = self.request.GET.get('source', '').strip()
        if source:
            queryset = queryset.filter(source=source)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Preserve filters for pagination links
        context['q'] = self.request.GET.get('q', '')
        context['source'] = self.request.GET.get('source', '')
        context['sources'] = Job.SOURCES
        return context


class JobDetailView(LoginRequiredMixin, DetailView):
    model = Job
    template_name = 'jobs/job_detail.html'
    context_object_name = 'job'


class JobFetchView(LoginRequiredMixin, View):
    """
    Triggers job discovery fetcher from APIs.
    """
    def post(self, request, *args, **kwargs):
        try:
            stats = JobFetcherService.fetch_all()
            total_fetched = sum(stats.values())
            
            message_details = ", ".join([f"{source.title()}: {count}" for source, count in stats.items()])
            if total_fetched > 0:
                messages.success(request, f"Successfully discovered {total_fetched} new jobs! ({message_details})")
            else:
                messages.info(request, "Job check complete. No new listings found at this time.")
                
        except Exception as e:
            messages.error(request, f"Error executing job discovery service: {str(e)}")
            
        return redirect('jobs:job_list')
