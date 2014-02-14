# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django import forms
from django.contrib.auth import authenticate, login
import logging
from ntulgapp.user import ntulgUserForm
from ntulgapp.globals import CURRENT_STAGE_NO
from ntulgapp.globals import CURRENT_STAGE_MANAGER
from ntulgapp.globals import CURRENT_STAGE_DATE

USER_INPUT_LEN_MIN = 1
USER_INPUT_LEN_MAX = 100

logger = logging.getLogger(__name__)

class loginForm(forms.Form):
    login_id = forms.CharField(required=False, label=u'帳號(account)', help_text=u'你的身份證字號(your ID.)', max_length=USER_INPUT_LEN_MAX)
    login_pw = forms.CharField(required=False, label=u'密碼(password)', max_length=USER_INPUT_LEN_MAX)

class signupForm(forms.Form):
    pass

def signup_view(request):
    def returnError(request, form, error):
        return render_to_response('signup.html',
                {
                    'form': form,
                    'error': error,
                    },
                context_instance=RequestContext(request)
                )
   
    if request.method == 'POST': # If the form has been submitted...
        form = ntulgUserForm(request.POST) # A form bound to the POST data
        post_keys = request.POST.keys()
        if u"confirm" in post_keys:
            if form.is_valid(): # All validation rules pass
                n = form.save()
                return HttpResponse('ok login')
            else:
                return returnError(request, form, u'資料輸入有誤，請檢查欄位，完成後請按\"確定\"！')
        elif u"cancel" in post_keys:
            #return HttpResponse('sign up')
            return render(request, 'home.html', {
                'form': loginForm})

    else:
        form = ntulgOldUserForm() # An unbound form

    return render(request, 'signup.html', {
        'form': form})

def signup_new_view(request):
    def returnError(request, form, error):
        return render_to_response('signup_new.html', {
            'form': form,
            'error': error,
            'stage_no': CURRENT_STAGE_NO,
            'stage_date': CURRENT_STAGE_DATE,
            'stage_manager': CURRENT_STAGE_MANAGER
            },
            context_instance=RequestContext(request)
            )

    if request.method == 'POST': # If the form has been submitted...
        new_post = request.POST.copy()
        new_post['stage_no'] = CURRENT_STAGE_NO
        new_post['cap_no'] = 0

        form = ntulgUserForm(new_post) # A form bound to the POST data
        form.fields['stage_no'].widget = forms.HiddenInput()
        form.fields['cap_no'].widget = forms.HiddenInput()
        
        post_keys = request.POST.keys()
        if u"confirm" in post_keys:
            if form.is_valid(): # All validation rules pass
                n = form.save()
                return render(request, 'signup_feedback.html', {'Email': new_post["email"]} )
            else:
                return returnError(request, form, u'資料輸入有誤，請檢查欄位，完成後請按\"確定\"！')
        elif u"cancel" in post_keys:
            return render(request, 'home.html', {
                'form': loginForm,
                'stage_no': CURRENT_STAGE_NO,
                'stage_date': CURRENT_STAGE_DATE,
                'stage_manager': CURRENT_STAGE_MANAGER})

    else:
        form = ntulgUserForm() # An unbound form
        form.fields['stage_no'].widget = forms.HiddenInput()
        form.fields['cap_no'].widget = forms.HiddenInput()


    return render(request, 'signup_new.html', {
        'form': form,
        'stage_no':CURRENT_STAGE_NO,
        'stage_date': CURRENT_STAGE_DATE,
        'stage_manager': CURRENT_STAGE_MANAGER})


def login_view(request):
    if request.method == 'POST': # If the form has been submitted...
        form = loginForm(request.POST) # A form bound to the POST data
        post_keys = request.POST.keys()
        logging.info(post_keys)
        if u"signin" in post_keys:
            if form.is_valid(): # All validation rules pass
                logging.info("valid")
                login_id = request.POST['login_id']
                login_pw = request.POST['login_pw']

                user = authenticate(username=login_id, password=login_pw)

                if user is not None:
                    if user.is_active:
                        return HttpResponse('ok login') 
                else:
                    return HttpResponse('bad login')
            else:
                logging.info("valid")
                return HttpResponse('bad login')

        elif u"signup" in post_keys:
            #return HttpResponse('sign up')
            return render(request, 'signup.html', {
                'form': ntulgUserForm})

        elif u"signup_new" in post_keys:
            form = ntulgUserForm() # An unbound form
            form.fields['stage_no'].widget = forms.HiddenInput()
            form.fields['cap_no'].widget = forms.HiddenInput()

            return render(request, 'signup_new.html', {
                'form': form,
                'stage_no':CURRENT_STAGE_NO,
                'stage_date': CURRENT_STAGE_DATE,
                'stage_manager': CURRENT_STAGE_MANAGER})

    else:
        form = loginForm() # An unbound form

    return render(request, 'home.html', {
        'form': form})
