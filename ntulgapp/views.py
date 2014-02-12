# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django import forms
from django.contrib.auth import authenticate, login
from ntulgapp.user import ntulgUser

USER_INPUT_LEN_MIN = 1
USER_INPUT_LEN_MAX = 100

class loginForm(forms.Form):
    login_id = forms.CharField(label=u'帳號', help_text=u'你的身份證字號', max_length=USER_INPUT_LEN_MAX)
    login_pw = forms.CharField(label=u'密碼', max_length=USER_INPUT_LEN_MAX)

class signupForm(forms.Form):
    pass

def signup_view(request):
    pass

def login_view(request):
    if request.method == 'POST': # If the form has been submitted...
        form = loginForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            login_id = request.POST['login_id']
            login_pw = request.POST['login_pw']

            user = authenticate(username=login_id, password=login_pw)

            if user is not None:
                if user.is_active:
                    #login(login_id, login_pw)
                    return HttpResponse('ok login') 
            else:
                return HttpResponse('bad login')
    else:
        form = loginForm() # An unbound form

    return render(request, 'home.html', {
        'form': form,
    })
