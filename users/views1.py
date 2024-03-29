"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import logging
from time import time
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, reverse
from django.contrib import auth
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.utils.http import is_safe_url
from rest_framework.authtoken.models import Token
from users import forms
from core.utils.common import load_func
from users.functions import login
from core.middleware import enforce_csrf_checks
from users.functions import proceed_registration
from organizations.models import Organization
from organizations.forms import OrganizationSignupForm
from users.models import User
from projects.models import Project


logger = logging.getLogger()


@login_required
def logout(request):
    auth.logout(request)
    if settings.HOSTNAME:
        redirect_url = settings.HOSTNAME
        if not redirect_url.endswith('/'):
            redirect_url += '/'
        return redirect(redirect_url)
    return redirect('/')



@enforce_csrf_checks
def user_signup(request):
    """ Sign up page
    """
    user = request.user
    next_page = request.GET.get('next')
    token = request.GET.get('token')

    # checks if the URL is a safe redirection.
    if not next_page or not is_safe_url(url=next_page, allowed_hosts=request.get_host()):
        next_page = reverse('projects:project-index')

    user_form = forms.UserSignupForm()
    organization_form = OrganizationSignupForm()

    if user.is_authenticated:
        return redirect(next_page)

    # make a new user
    if request.method == 'POST':
        organization = Organization.objects.first()
        if settings.DISABLE_SIGNUP_WITHOUT_LINK is True:
            if not(token and organization and token == organization.token):
                raise PermissionDenied()
        else:
            if token and organization and token != organization.token:
                raise PermissionDenied()

        user_form = forms.UserSignupForm(request.POST)
        organization_form = OrganizationSignupForm(request.POST)

        if user_form.is_valid():
            redirect_response = proceed_registration(request, user_form, organization_form, next_page)
            if redirect_response:
                return redirect_response

    return render(request, 'users/user_signup.html', {
        'user_form': user_form,
        'organization_form': organization_form,
        'next': next_page,
        'token': token,
    })


@enforce_csrf_checks
def user_login(request):
    """ Login page
    """
    user = request.user
    next_page = request.GET.get('next')

    # checks if the URL is a safe redirection.
    if not next_page or not is_safe_url(url=next_page, allowed_hosts=request.get_host()):
        next_page = reverse('projects:project-index')

    login_form = load_func(settings.USER_LOGIN_FORM)
    form = login_form()

    if user.is_authenticated:
        return redirect(next_page)

    if request.method == 'POST':
        form = login_form(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            if form.cleaned_data['persist_session'] is not True:
                # Set the session to expire when the browser is closed
                request.session['keep_me_logged_in'] = False
                request.session.set_expiry(0)

            # user is organization member
            org_pk = Organization.find_by_user(user).pk
            user.active_organization_id = org_pk
            user.save(update_fields=['active_organization'])
            return redirect(next_page)

    return render(request, 'users/user_login.html', {
        'form': form,
        'next': next_page
    })





##################
from label_studio_sdk import Client
import json
from django.http import HttpResponse
LABEL_STUDIO_URL = 'http://127.0.0.1:8081/'

@enforce_csrf_checks
def user_auth(request):
    email = request.GET.get('email')
    assign = request.GET.get('assign')
    password = '12345678'
    next_page = reverse('projects:project-index')

    # admin
    if email == 'aaa@gmail.com':
        user = User.objects.get(email=email)
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        if  assign=='yes':
            return redirect("assign_project")
        else:
            return redirect(next_page)

    # user
    try:
        user = User.objects.get(email=email)
        API_KEY = user.auth_token
        ls = Client(url=LABEL_STUDIO_URL, api_key=str(API_KEY))
        projects = ls.get_projects()
        task_urls = []
        for project in projects:
            tasks = project.get_tasks()
            for task in tasks:
                task_id = task["id"]
                task_url = f'{LABEL_STUDIO_URL}projects/{str(project.id)}/data?tab=&task={str(task_id)}'
                completed_at = task["completed_at"]
                created_at = task["created_at"]
                updated_at = task["updated_at"]
                task_urls.append(
                    {
                        "task_id": task_id,
                        "task_url": task_url,
                        "completed_at": completed_at,
                        "created_at" : created_at,
                        "updated_at" : updated_at,
                    }
                )
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return HttpResponse(json.dumps(task_urls))
        # return redirect(next_page)

    except:
            organization_form = OrganizationSignupForm()
            user_form = forms.UserSignupForm({'email': email, 'password': password})
            if user_form.is_valid():
                proceed_registration(request, user_form, organization_form, next_page)
                user = User.objects.get(email=email)
                API_KEY = user.auth_token
                ls = Client(url=LABEL_STUDIO_URL, api_key=str(API_KEY))
                projects = ls.get_projects()
                task_urls = []
                for project in projects:
                    tasks = project.get_tasks()
                    for task in tasks:
                        task_id = task["id"]
                        task_url = f'{LABEL_STUDIO_URL}projects/{str(project.id)}/data?tab=&task={str(task_id)}'
                        completed_at = task["completed_at"]
                        created_at = task["created_at"]
                        updated_at = task["updated_at"]
                        task_urls.append(
                            {
                                "task_id": task_id,
                                "task_url": task_url,
                                "completed_at": completed_at,
                                "created_at" : created_at,
                                "updated_at" : updated_at,
                            }
                        )
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return HttpResponse(json.dumps(task_urls))
###################



###########$$$$$$$$$$$
@enforce_csrf_checks
def user_signin(request):
    email = request.GET.get('email')
    password = '12345678'
    next_page = reverse('projects:project-index')
    # user
    try:
        user = User.objects.get(email=email)
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return HttpResponse("<h1>You Logged In Successfully</h1>")
        # return redirect(next_page)

    except:
            organization_form = OrganizationSignupForm()
            user_form = forms.UserSignupForm({'email': email, 'password': password})
            if user_form.is_valid():
                proceed_registration(request, user_form, organization_form, next_page)
                user = User.objects.get(email=email)
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return HttpResponse("<h1>You Logged In Successfully</h1>")
###################



@login_required
def user_account(request):
    user = request.user

    if user.active_organization is None and 'organization_pk' not in request.session:
        return redirect(reverse('main'))

    form = forms.UserProfileForm(instance=user)
    token = Token.objects.get(user=user)

    if request.method == 'POST':
        form = forms.UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect(reverse('user-account'))
        
    return render(request, 'users/user_account.html', {
        'settings': settings,
        'user': user,
        'user_profile_form': form,
        'token': token
    })
