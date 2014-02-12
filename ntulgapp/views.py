# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django import forms
from django.contrib.auth import authenticate, login
import logging
from ntulgapp.user import ntulgUserForm

USER_INPUT_LEN_MIN = 1
USER_INPUT_LEN_MAX = 100

logger = logging.getLogger(__name__)

class loginForm(forms.Form):
    login_id = forms.CharField(required=False, label=u'帳號(account)', help_text=u'你的身份證字號(your ID)', max_length=USER_INPUT_LEN_MAX)
    login_pw = forms.CharField(required=False, label=u'密碼(password)', max_length=USER_INPUT_LEN_MAX)

class signupForm(forms.Form):
    pass

def signup_view(request):
    pass

def login_view(request):
    if request.method == 'POST': # If the form has been submitted...
        form = loginForm(request.POST) # A form bound to the POST data
        post_keys = request.POST.keys()
        if u"signin" in post_keys:
            if form.is_valid(): # All validation rules pass
                login_id = request.POST['login_id']
                login_pw = request.POST['login_pw']

                user = authenticate(username=login_id, password=login_pw)

                if user is not None:
                    if user.is_active:
                        return HttpResponse('ok login') 
                else:
                    return HttpResponse('bad login')
        elif u"signup" in post_keys:
            #return HttpResponse('sign up')
            return render(request, 'signup.html', {
                'form': ntulgUserForm})

    else:
        form = loginForm() # An unbound form
    return render(request, 'home.html', {
        'form': form,
    })
