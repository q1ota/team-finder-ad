from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from users.service import paginate

from .constants import PROJECTS_PER_PAGE, STATUS_CLOSED, STATUS_OPEN
from .forms import ProjectForm
from .models import Project


def project_list(request):
    projects = Project.objects.select_related('owner').prefetch_related('participants').order_by('-created_at')
    page_obj = paginate(projects, PROJECTS_PER_PAGE, request)
    return render(request, 'projects/project_list.html', {
        'page_obj': page_obj,
        'query_prefix': '',
    })


def project_detail(request, pk):
    project = get_object_or_404(
        Project.objects.select_related('owner').prefetch_related('participants'), pk=pk
    )
    return render(request, 'projects/project-details.html', {'project': project})


@login_required
def project_create(request):
    form = ProjectForm(request.POST or None)
    if form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        project.participants.add(request.user)
        return redirect(reverse('projects:project_detail', kwargs={'pk': project.pk}))
    return render(request, 'projects/create-project.html', {'form': form, 'is_edit': False})


@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner != request.user and not request.user.is_staff:
        return redirect(reverse('projects:project_detail', kwargs={'pk': pk}))
    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        form.save()
        return redirect(reverse('projects:project_detail', kwargs={'pk': pk}))
    return render(request, 'projects/create-project.html', {'form': form, 'is_edit': True})


@login_required
def project_complete(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=HTTPStatus.METHOD_NOT_ALLOWED)
    project = get_object_or_404(Project, pk=pk)
    if project.owner != request.user:
        return JsonResponse({'error': 'Forbidden'}, status=HTTPStatus.FORBIDDEN)
    if project.status != STATUS_OPEN:
        return JsonResponse({'error': 'Already closed'}, status=HTTPStatus.BAD_REQUEST)
    project.status = STATUS_CLOSED
    project.save()
    return JsonResponse({'status': 'ok', 'project_status': STATUS_CLOSED})


@login_required
def toggle_participate(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=HTTPStatus.METHOD_NOT_ALLOWED)
    project = get_object_or_404(Project, pk=pk)
    user = request.user
    if already := project.participants.filter(pk=user.pk).exists():
        project.participants.remove(user)
    else:
        project.participants.add(user)
    return JsonResponse({'status': 'ok', 'participant': not already})
