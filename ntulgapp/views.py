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
from ntulgapp.globals import CURRENT_STAGE
from ntulgapp.globals import APP_URL
from django.contrib.auth.models import User
import string
import random
from google.appengine.api import mail

USER_INPUT_LEN_MIN = 1
USER_INPUT_LEN_MAX = 100

logger = logging.getLogger(__name__)

def auto_fill(post_data):
    new_post_data = post_data.copy()
    new_post_data['stage_no'] = 99
    new_post_data['cap_no'] = 889
    new_post_data['name_cht'] = u"陳田富"
    new_post_data['name_eng'] = u"CHEN,TIENFU"
    new_post_data['nationality']= u"TW"
    #new_post_data['identify_number']= u"E122112091"
    new_post_data['email']=u"tim.chen.86@gmail.com"
    new_post_data['birthday']=u"1980-2-2"
    new_post_data['sex']=u"male"
    new_post_data['tel_mobile']=u"0937019827"
    new_post_data['tel']=u"(02)22222222"
    new_post_data['address']=u"12313 基隆市中正區正義路40號"
    new_post_data['height']=177
    new_post_data['weight']=65
    new_post_data['tshirt_size']=u"M"
    new_post_data['if_present_ntu']=True
    new_post_data['if_vegetarian']=False
    new_post_data['emergency_contact_name']=u"我"
    new_post_data['emergency_contact_mobile']=u"0928371231"
    new_post_data['beneficiary']=u"他"
    new_post_data['beneficiary_relationship']=u"兄弟"
    new_post_data['medical_history']=u"無"
    new_post_data['source']=u"faceook看到的"
    #new_post_data['comment']=
    #new_post_data['facebook_id']=
    #new_post_data['ptt_id']=
    #new_post_data['ptt2_id']=
    
    return new_post_data


def create_user(user_title, user_name, email):
    password = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(8))

    if User.objects.filter(username=user_name).count():
        return False

    user = User.objects.create_user(user_name, email, password)
    user.save()
    body = u"%s 你好，\n你的密碼是：%s\n\n管理系統：%s" % (user_title, password, APP_URL)
    #mail.send_mail(sender="tim.chen.86@gmail.com",to=email,subject=u"謝謝使用台大救生班隊員資料管理系統", body=body)

    return True

class loginForm(forms.Form):
    login_id = forms.CharField(required=False, label=u'帳號(account)', help_text=u'你的身份證字號/居留證號碼(your ID.)', max_length=USER_INPUT_LEN_MAX)
    login_pw = forms.CharField(required=False, label=u'密碼(password)', max_length=USER_INPUT_LEN_MAX)


def signup_view(request, if_training):
    def returnError(request, form, error):
        return render_to_response('signup.html',
                {
                    'form': form,
                    'error': error,
                    },
                context_instance=RequestContext(request)
                )
   
    if request.method == 'POST': # If the form has been submitted...
        #   new_post = request.POST.copy()

        new_post = auto_fill(request.POST)
        form = ntulgUserForm(new_post) # A form bound to the POST data
        
        if if_training:
            form.fields['stage_no'].widget = forms.HiddenInput()
            form.fields['cap_no'].widget = forms.HiddenInput()

        post_keys = request.POST.keys()
        if u"confirm" in post_keys:
            if form.is_valid(): # All validation rules pass
                n = form.save()
                if create_user(new_post['name_cht'], new_post['identify_number'], new_post['email']):
                    return render_to_response('signup_feedback.html', {'Email': new_post["email"]},context_instance=RequestContext(request) )
                else:
                    return returnError(request, form, u'你已經註冊過了，請直接登入，或再次檢查你所輸入的身分證字號，或聯絡管理員！')

            else:
                return returnError(request, form, u'資料輸入有誤，請檢查欄位，完成後請按\"確定\"！')

        elif u"cancel" in post_keys:
            return render_to_response('home.html',{'form':loginForm},context_instance=RequestContext(request))

    else:
        form = ntulgUserForm() # An unbound form
        if if_training:
            form.fields['stage_no'].widget = forms.HiddenInput()
            form.fields['cap_no'].widget = forms.HiddenInput()
        return render_to_response('signup.html',{
            'form':form,
            'if_training':if_training
            },context_instance=RequestContext(request))

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
            form = ntulgUserForm() # An unbound form
            param = {
            'form': form,
            'signup_training':  False
            }

            return render_to_response('signup.html', param)

        elif u"signup_new" in post_keys:
            form = ntulgUserForm() # An unbound form
            form.fields['stage_no'].widget = forms.HiddenInput()
            form.fields['cap_no'].widget = forms.HiddenInput()
            param = {
            'form': form,
            'signup_training': True, 
            'stage_no':CURRENT_STAGE_NO,
            'stage_date': CURRENT_STAGE_DATE,
            'stage_manager': CURRENT_STAGE_MANAGER}

            return render_to_response('signup.html', param)

    else:
        form = loginForm() # An unbound form

    return render(request, 'home.html', {
        'form': form})
