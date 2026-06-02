import json

from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CustomPasswordChangeForm, EditProfileForm, LoginForm, RegisterForm
from .models import Skill, User


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            user = User.objects.create_user(
                email=d['email'],
                name=d['name'],
                surname=d['surname'],
                password=d['password'],
            )
            login(request, user)
            return redirect('/projects/list/')
        return render(request, 'users/register.html', {'form': form})
    form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            login(request, form.cleaned_data['user'])
            return redirect('/projects/list/')
        return render(request, 'users/login.html', {'form': form})
    form = LoginForm()
    return render(request, 'users/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('/projects/list/')


def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    return render(request, 'users/user-details.html', {'user': user})


def user_list(request):
    skill_name = request.GET.get('skill', '').strip()
    users = User.objects.filter(is_active=True).order_by('id')
    all_skills = Skill.objects.values_list('name', flat=True).order_by('name')
    active_skill = None
    query_prefix = ''

    if skill_name:
        skill_obj = Skill.objects.filter(name=skill_name).first()
        if skill_obj:
            users = users.filter(skills=skill_obj)
            active_skill = skill_name
            query_prefix = f'skill={skill_name}&'

    paginator = Paginator(users, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'users/participants.html', {
        'page_obj': page_obj,
        'all_skills': all_skills,
        'active_skill': active_skill,
        'query_prefix': query_prefix,
    })


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect(f'/users/{request.user.pk}/')
        return render(request, 'users/edit_profile.html', {'form': form})
    form = EditProfileForm(instance=request.user)
    return render(request, 'users/edit_profile.html', {'form': form})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect(f'/users/{request.user.pk}/')
        return render(request, 'users/change_password.html', {'form': form})
    form = CustomPasswordChangeForm(request.user)
    return render(request, 'users/change_password.html', {'form': form})


def skills_autocomplete(request):
    q = request.GET.get('q', '').strip()
    skills = Skill.objects.filter(name__istartswith=q).values('id', 'name')[:10]
    return JsonResponse(list(skills), safe=False)


@login_required
def skill_add(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    user = get_object_or_404(User, pk=pk)
    if user != request.user:
        return JsonResponse({'error': 'Forbidden'}, status=403)

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        body = request.POST

    skill_id = body.get('skill_id')
    name = (body.get('name') or '').strip()
    created = False

    if skill_id:
        skill = get_object_or_404(Skill, pk=skill_id)
    elif name:
        skill, created = Skill.objects.get_or_create(name=name)
    else:
        return JsonResponse({'error': 'skill_id or name required'}, status=400)

    added = skill not in user.skills.all()
    if added:
        user.skills.add(skill)

    return JsonResponse({
        'id': skill.pk,
        'name': skill.name,
        'skill_id': skill.pk,
        'created': created,
        'added': added,
    })


@login_required
def skill_remove(request, pk, skill_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    user = get_object_or_404(User, pk=pk)
    if user != request.user:
        return JsonResponse({'error': 'Forbidden'}, status=403)

    skill = get_object_or_404(Skill, pk=skill_id)
    if skill not in user.skills.all():
        return JsonResponse({'error': 'Skill not in profile'}, status=400)

    user.skills.remove(skill)
    return JsonResponse({'status': 'ok'})
