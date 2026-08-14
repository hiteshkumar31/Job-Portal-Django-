from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_POST
from django.views.generic import (ListView, DetailView, CreateView, UpdateView, DeleteView)
from django.urls import reverse, reverse_lazy

from .models import Job, Application
from .forms import Jobform


# ============================================================
# JOB LIST
# Both Job Seeker and Employer can view jobs
# ============================================================

class JobListView(ListView):
    model = Job
    template_name = 'job_list.html'
    context_object_name = 'all_jobs'
    paginate_by = 6

    def get_queryset(self):
        queryset = Job.objects.all()

        # Search by role or title
        search = self.request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(title__icontains=search)

        # Locaiton filter
        location = self.request.GET.get('location', '').strip()
        if location:
            queryset = queryset.filter(location__icontains=location)
        
        company_name = self.request.GET.get('company_name', '').strip()
        if company_name:
            queryset = queryset.filter(company_name__icontains=company_name)

        return queryset.order_by('-date_posted')


# ============================================================
# JOB DETAIL
# Both Job Seeker and Employer can view job details
# ============================================================

class JobDetailView(DetailView):
    model = Job
    template_name = 'job_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:

            # Is current user the owner of this job?
            context['is_owner'] = (
                self.object.posted_by == self.request.user
            )

            # Is current user already applied?
            context['already_applied'] = Application.objects.filter(
                job=self.object,
                applicant=self.request.user
            ).exists()

        return context


# ============================================================
# CREATE JOB
# ONLY EMPLOYER
# ============================================================

class JobCreateView(LoginRequiredMixin, CreateView):
    model = Job
    form_class = Jobform
    template_name = 'job_form.html'

    def dispatch(self, request, *args, **kwargs):

        if request.user.role != 'employer':
            messages.error(
                request,
                'Only employers can post jobs.'
            )

            return redirect('job-list')

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):

        # Automatically set logged-in employer as job owner
        form.instance.posted_by = self.request.user

        return super().form_valid(form)

    def get_success_url(self):

        return reverse(
            'job-detail',
            kwargs={'pk': self.object.pk}
        )


# ============================================================
# UPDATE JOB
# ONLY EMPLOYER + JOB OWNER
# ============================================================

class JobUpdateView(LoginRequiredMixin, UpdateView):
    model = Job
    form_class = Jobform
    template_name = 'job_form.html'

    def dispatch(self, request, *args, **kwargs):

        if request.user.role != 'employer':
            messages.error(
                request,
                'Only employers can edit jobs.'
            )

            return redirect('job-list')

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):

        # Employer can edit ONLY their own jobs
        return Job.objects.filter(
            posted_by=self.request.user
        )

    def get_success_url(self):

        return reverse(
            'job-detail',
            kwargs={'pk': self.object.pk}
        )


# ============================================================
# DELETE JOB
# ONLY EMPLOYER + JOB OWNER
# ============================================================

class JobDeleteView(LoginRequiredMixin, DeleteView):
    model = Job
    template_name = 'job_confirm_delete.html'
    success_url = reverse_lazy('my-jobs')

    def dispatch(self, request, *args, **kwargs):

        if request.user.role != 'employer':
            messages.error(
                request,
                'Only employers can delete jobs.'
            )

            return redirect('job-list')

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):

        # Employer can delete ONLY their own jobs
        return Job.objects.filter(
            posted_by=self.request.user
        )


# ============================================================
# MY POSTED JOBS
# ONLY EMPLOYER
# ============================================================

class MyJobsListView(LoginRequiredMixin, ListView):
    model = Job
    template_name = 'my_jobs_list.html'
    context_object_name = 'jobs'

    paginate_by = 5

    def dispatch(self, request, *args, **kwargs):

        if request.user.role != 'employer':
            messages.error(
                request,
                'Only employers can access posted jobs.'
            )

            return redirect('job-list')

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):

        # Show ONLY current employer's jobs
        return Job.objects.filter(
            posted_by=self.request.user
        )


# ============================================================
# APPLY TO JOB
# ONLY JOB SEEKER
# ============================================================

@login_required
@require_POST
def apply_to_job(request, pk):

    if request.user.role != 'seeker':
        messages.error(
            request,
            'Only job seekers can apply for jobs.'
        )
        return redirect('job-detail', pk=pk)

    job = get_object_or_404(Job, pk=pk)

    if job.posted_by == request.user:
        messages.error(
            request,
            'You cannot apply to your own job posting.'
        )
        return redirect('job-detail', pk=job.pk)

    application, created = Application.objects.get_or_create(
        job=job,
        applicant=request.user
    )

    if created:
        messages.success(
            request,
            f'You applied to "{job.title}".'
        )
    else:
        messages.info(
            request,
            'You have already applied to this job.'
        )

    return redirect('job-detail', pk=job.pk)

# ============================================================
# MY APPLICATIONS
# ONLY JOB SEEKER
# ============================================================

class MyApplicationsListView(LoginRequiredMixin, ListView):
    model = Application
    template_name = 'my_applications_list.html'
    context_object_name = 'applications'

    paginate_by = 5

    def dispatch(self, request, *args, **kwargs):

        if request.user.role != 'seeker':
            messages.error(
                request,
                'Only job seekers can access their applications.'
            )

            return redirect('job-list')

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):

        return Application.objects.filter(applicant=self.request.user).select_related('job').order_by('-date_applied')


# ============================================================
# VIEW APPLICANTS
# ONLY EMPLOYER + JOB OWNER
# ============================================================

@login_required
def job_applicants(request, pk):

    # Only employer can view applicants
    if request.user.role != 'employer':

        messages.error(
            request,
            'Only employers can view applicants.'
        )

        return redirect('job-list')

    job = get_object_or_404(
        Job,
        pk=pk
    )

    # Only the employer who posted this job
    # can view its applicants
    if job.posted_by != request.user:

        messages.error(
            request,
            'You are not allowed to view applicants for this job.'
        )

        return redirect(
            'job-list'
        )

    applications = Application.objects.filter(
        job=job
    ).select_related(
        'applicant',
        'applicant__profile'
    ).order_by(
        '-date_applied'
    )

    return render(
        request,
        'job_applicants.html',
        {
            'job': job,
            'applications': applications,
        }
    )


# ============================================================
# UPDATE APPLICATION STATUS
# ONLY EMPLOYER + JOB OWNER
# ============================================================

@login_required
@require_POST
def update_application_status(
    request,
    application_id
):

    # Only employer can change status
    if request.user.role != 'employer':

        messages.error(
            request,
            'Only employers can update application status.'
        )

        return redirect(
            'job-list'
        )

    application = get_object_or_404(
        Application.objects.select_related(
            'job',
            'applicant'
        ),
        pk=application_id
    )

    # Only job owner can update application
    if application.job.posted_by != request.user:

        messages.error(
            request,
            'You are not allowed to update this application.'
        )

        return redirect(
            'job-list'
        )

    status = request.POST.get(
        'status'
    )

    # Get valid statuses from model
    valid_statuses = dict(
        Application.STATUS_CHOICES
    )

    # Validate status
    if status not in valid_statuses:

        messages.error(
            request,
            'Invalid application status.'
        )

        return redirect(
            'job-applicants',
            pk=application.job.pk
        )

    # Update status
    application.status = status

    application.save()

    messages.success(
        request,
        f'Application status updated to '
        f'"{valid_statuses[status]}".'
    )

    return redirect(
        'job-applicants',
        pk=application.job.pk
    )

# ============================================================
# EMPLOYER DASHBOARD
# ============================================================

# ============================================================
# EMPLOYER DASHBOARD
# ============================================================

@login_required
def employer_dashboard(request):

    # Only employers can access dashboard
    if request.user.role != 'employer':
        messages.error(
            request,
            'Only employers can access the employer dashboard.'
        )
        return redirect('job-list')

    # Get jobs posted by current employer
    jobs = Job.objects.filter(
        posted_by=request.user
    ).order_by('-date_posted')

    # Total jobs posted by employer
    total_jobs = jobs.count()

    # Get all applications for employer's jobs
    applications = Application.objects.filter(
        job__posted_by=request.user
    )

    # Total applications
    total_applications = applications.count()

    # Total interview invitations
    total_interviews = applications.filter(
        status='interview'
    ).count()

    # Total hired candidates
    total_hired = applications.filter(
        status='hired'
    ).count()

    # Total rejected candidates
    total_rejected = applications.filter(
        status='rejected'
    ).count()

    # Send data to template
    context = {
        'jobs': jobs,
        'total_jobs': total_jobs,
        'total_applications': total_applications,
        'total_interviews': total_interviews,
        'total_hired': total_hired,
        'total_rejected': total_rejected,
    }

    return render(
        request,
        'employer_dashboard.html',
        context
    )