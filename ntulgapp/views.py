# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django import forms

USER_INPUT_LEN_MIN = 1
USER_INPUT_LEN_MAX = 100

class loginForm(forms.Form):
    login_id = forms.CharField(label=u'帳號', help_text=u'你的身份證字號', max_length=USER_INPUT_LEN_MAX)
    login_pw = forms.CharField(label=u'密碼', max_length=USER_INPUT_LEN_MAX)


def login(request):
    if request.method == 'POST': # If the form has been submitted...
        form = loginForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            # ...
            #return HttpResponseRedirect('/thanks/') # Redirect after POST
            return HttpResponse('thanks')
    else:
        form = loginForm() # An unbound form

    return render(request, 'home.html', {
        'form': form,
    })
