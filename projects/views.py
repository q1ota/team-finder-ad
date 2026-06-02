import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProjectForm
from .models import Project


def project_list(request):
    projects = Project.objects.select_related('owner').order_by('-created_at')
    paginator = Paginator(projects, 12)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'projects/project_list.html', {
        'page_obj': page_obj,
        'query_prefix': '',
    })


def project_detail(request, pk):
    project = get_object_or_404(
        Project.objects.prefetch_related('participants', 'owner'), pk=pk
    )
    return render(request, 'projects/project-details.html', {'project': project})


@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            return redirect(f'/projects/{project.pk}/')
        return render(request, 'projects/create-project.html', {'form': form, 'is_edit': False})
    form = ProjectForm()
    return render(request, 'projects/create-project.html', {'form': form, 'is_edit': False})


@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner != request.user and not request.user.is_staff:
        return redirect(f'/projects/{pk}/')
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect(f'/projects/{pk}/')
        return render(request, 'projects/create-project.html', {'form': form, 'is_edit': True})
    form = ProjectForm(instance=project)
    return render(request, 'projects/create-project.html', {'form': form, 'is_edit': True})


@login_required
def project_complete(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    project = get_object_or_404(Project, pk=pk)
    if project.owner != request.user:
        return JsonResponse({'error': 'Forbidden'}, status=403)
    if project.status != 'open':
        return JsonResponse({'error': 'Already closed'}, status=400)
    project.status = 'closed'
    project.save()
    return JsonResponse({'status': 'ok', 'project_status': 'closed'})


@login_required
def toggle_participate(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    project = get_object_or_404(Project, pk=pk)
    user = request.user
    if project.participants.filter(pk=user.pk).exists():
        project.participants.remove(user)
        joined = False
    else:
        project.participants.add(user)
        joined = True
    return JsonResponse({'status': 'ok', 'participant': joined})
