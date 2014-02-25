# -*- coding: utf-8 -*-
import re
import pprint
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django import forms
from django.contrib.auth import authenticate, login
import logging
from ntulifeguardapp.user import ntulgUser
from ntulifeguardapp.user import ntulgUserForm
from ntulifeguardapp.user import ntulgUserUpdateForm
from ntulifeguardapp.globals import CURRENT_STAGE
from ntulifeguardapp.globals import APP_LOGIN_MAX_RETRY
from ntulifeguardapp.globals import APP_EMAIL_GREETING
from ntulifeguardapp.globals import APP_URL
from ntulifeguardapp.globals import APP_IMG_UPLOADER_URL
from ntulifeguardapp.globals import APP_ADMIN_EMAIL
from ntulifeguardapp.globals import APP_NOTICE_EMAIL
from ntulifeguardapp.globals import APP_SPREADSHEET_ID
from ntulifeguardapp.globals import APP_SPREADSHEET_WORKSHEET_ID
from ntulifeguardapp.spreadsheet import buildSpreadsheetService 
from django.contrib.auth.models import User
import string
import random
from google.appengine.api import mail
from django.shortcuts import redirect

import gdata.spreadsheet

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
    #new_post_data['id_number']= u"K123123123"
    #new_post_data['email']=u"tim.chen.86@gmail.com"
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



def post_to_spreadsheet(post):
    post.pop("csrfmiddlewaretoken")
    post.pop("confirm")
    post.pop("cap_no")
 
    # as spreadsheet header name can't contain '_' char
    for key in post:
        new_key = key.replace("_", "-")
        post[new_key] = post.pop(key)[0]

    service = buildSpreadsheetService()

    if service:
        entry = service.InsertRow(post, APP_SPREADSHEET_ID, APP_SPREADSHEET_WORKSHEET_ID)
        if isinstance(entry, gdata.spreadsheet.SpreadsheetsList):           
            logging.info("%s ok" % __name__)
        else:
            logging.info("%s failed" % __name__)


def levenshtein(s1, s2):
    l1 = len(s1)
    l2 = len(s2)

    matrix = [range(l1 + 1)] * (l2 + 1)
    for zz in range(l2 + 1):
        matrix[zz] = range(zz,zz + l1 + 1)
    for zz in range(0,l2):
        for sz in range(0,l1):
            if s1[sz] == s2[zz]:
                matrix[zz+1][sz+1] = min(matrix[zz+1][sz] + 1, matrix[zz][sz+1] + 1, matrix[zz][sz])
            else:
                matrix[zz+1][sz+1] = min(matrix[zz+1][sz] + 1, matrix[zz][sz+1] + 1, matrix[zz][sz] + 1)
    return matrix[l2][l1]

def create_user(user_title, user_name, email):
    #password = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(8))
    password = ''.join(random.choice(string.ascii_letters + string.digits + string.punctuation) for x in range(12))
    logging.info("user_name=%s, password=%s" % (user_name, password))
    
    try:
        User.objects.get(username=user_name)

    except User.DoesNotExist:
        user = User.objects.create_user(user_name, email, password)

        if user:
            user.save()

            body = u"%s 你好，\n你的密碼是：%s\n\n請由此登入管理系統：%s" % (user_title, password, APP_URL)

            try:
                mail.send_mail(sender=APP_ADMIN_EMAIL,to=email,subject=APP_EMAIL_GREETING, body=body)
            except:
                pass
            return user

        else: 
            return None

    else:
        return None

class updatePasswordForm(forms.Form):
    old_pw = forms.CharField(required=False, label=u'舊密碼(old password)', max_length=USER_INPUT_LEN_MAX)
    new_pw = forms.CharField(required=False, label=u'新密碼(new password)', max_length=USER_INPUT_LEN_MAX)
    new_pw_confirm = forms.CharField(required=False, label=u'再次輸入新密碼(new password again)', max_length=USER_INPUT_LEN_MAX)

class loginForm(forms.Form):
    login_id = forms.CharField(required=False, label=u'帳號(account)', help_text=u'你的身分證字號/居留證號碼(your ID.)', max_length=USER_INPUT_LEN_MAX)
    login_pw = forms.CharField(required=False, label=u'密碼(password)', max_length=USER_INPUT_LEN_MAX)

def signup_view(request, if_training):

    if request.method == 'POST': # If the form has been submitted...
        logging.info(request.POST)
        new_post = request.POST.copy()
        new_post["id_number"] = new_post.get("id_number").upper()
        
        if if_training:
            new_post["stage_no"] = str(CURRENT_STAGE["no"])

        form = ntulgUserForm(new_post) # A form bound to the POST data
        if if_training:
            form.fields['stage_no'].widget = forms.HiddenInput()
            form.fields['cap_no'].widget = forms.HiddenInput()

        post_keys = request.POST.keys()

        if u"confirm" in post_keys:
            if form.is_valid(): # All validation rules pass
                user = create_user(new_post['name_cht'], new_post['id_number'], new_post['email'])
                if user is not None:
                    n = form.save()
                    post_to_spreadsheet(new_post)
                    return render_to_response('signup_feedback.html', {'Email': new_post["email"], 'subject':APP_EMAIL_GREETING},context_instance=RequestContext(request) )
                else:
                    return render(request, 'signup.html', {
                        'form':form,
                        'if_training':if_training,
                        'error':u'你已經註冊過了，請直接登入，或再次檢查你所輸入的身分證字號，或聯絡管理員！'},
                        context_instance=RequestContext(request))

            else:
                return render(request, 'signup.html', {
                    'form':form,
                    'if_training':if_training,
                    'error':u'資料輸入有誤，請檢查欄位，完成後請按\"確定\"！'},
                    context_instance=RequestContext(request))

        elif u"cancel" in post_keys:
            return redirect("/")

    else:
        form = ntulgUserForm() # An unbound form
        if if_training:
            form.fields['stage_no'].widget = forms.HiddenInput()
            form.fields['cap_no'].widget = forms.HiddenInput()
        return render_to_response('signup.html',{
            'form':form,
            'uploader_url':APP_IMG_UPLOADER_URL,
            'if_training':if_training
            },context_instance=RequestContext(request))

def management_view(request):
    logging.info("management_view")
    
    q_user = request.session.get("q_user")

    #logging.info(q_user)
    post_keys = request.POST.keys()

    if q_user is not None: # If the form has been submitted...
        logging.info(q_user.id)
        logging.info(q_user.id_number)

        if u"update_data" in post_keys:
            form = ntulgUserUpdateForm(instance=q_user)
            #form = ntulgUserForm(instance=q_user)
            return render_to_response('update_data.html', {
            'uploader_url':APP_IMG_UPLOADER_URL+q_user.id_number,
            'form':form}, context_instance=RequestContext(request))

        elif u"update_password" in post_keys:
            form = updatePasswordForm()
            return render(request, 'update_password.html', {'form':form}, context_instance=RequestContext(request))
        elif u"logout" in post_keys:
            request.session.flush()
            return redirect("/")
        else: 
            return render_to_response('management.html',context_instance=RequestContext(request))
    else:
        return redirect("/")

def check_new_password(old_pw, new_pw):
    result_re = re.match("^(?=.*?[a-zA-Z])(?=.*?[0-9]).{8,}$",new_pw)

    result_levenshtein = levenshtein(new_pw, old_pw) 

    logging.info("check_new_password old: %s, new: %s" % (old_pw, new_pw))
    logging.info("check_new_password re: %s", result_re)
    logging.info("check_new_password levenshtein: %s", result_levenshtein)

    if (result_re is not None) and (result_levenshtein > 5):
        return True
    else:
        return False

def update_password_view(request): #, user_name=None):
    q_user = request.session.get("q_user")
    logging.info(q_user)
    logging.info(dir(q_user))
    if request.method == 'POST': # If the form has been submitted...
       
        post_keys = request.POST.keys()
        if u"confirm" in post_keys:
            form = updatePasswordForm(request.POST)

            old_pw = request.POST.get(u'old_pw')
            new_pw = request.POST.get(u'new_pw')
            new_pw_confirm = request.POST.get(u'new_pw_confirm')

            user = authenticate(username=q_user.id_number, password=old_pw)

            if user is not None and user.is_active:
                #return render_to_response('update_data.html', {'form':q_form, 'error':u"表單錯誤請檢查"}, context_instance=RequestContext(request))
                if new_pw == new_pw_confirm:
                    if check_new_password(old_pw, new_pw):
                        user.set_password(new_pw)
                        user.save()
                        return render_to_response('management.html', {'info':u"密碼更新完成，下次登入系統時請使用新密碼。"}, context_instance=RequestContext(request))
                    else:
                        return render_to_response('update_password.html', {'form': form, 'error':u"新密碼不符合規則，請重新輸入。"}, context_instance=RequestContext(request))

                else:
                    return render_to_response('update_password.html', {'form': form, 'error':u"兩組新密碼不一致"}, context_instance=RequestContext(request))

            else:
                return render_to_response('update_password.html', {'form':form, 'error':u"舊密碼錯誤，請檢查"}, context_instance=RequestContext(request))

        elif u"cancel" in post_keys:
            return redirect("/management")
            
    else:
        return redirect("/")


def update_data_view(request):
    if request.method == 'POST': # If the form has been submitted...
        new_post = request.POST.copy()

        q_user_temp = ntulgUser.objects.filter(id_number=new_post.get("id_number"))
        if q_user_temp is not None:
            q_user = q_user_temp[0]
        else:
            return redirect("/")

        q_form = ntulgUserUpdateForm(new_post, instance=q_user)
        #q_form = ntulgUserForm(new_post, instance=q_user)

        logging.info(q_user.id)
        logging.info(q_user.id_number)
        
        post_keys = request.POST.keys()
        if u"confirm" in post_keys:
            if q_form.is_valid():
                logging.info("confirm update")
                logging.info(new_post)

                user_model = q_form.save()
                request.session["q_user"] = user_model

                return redirect("/management")
            else:
                return render_to_response('update_data.html', {'form':q_form, 'error':u"表單錯誤請檢查"}, context_instance=RequestContext(request))

        elif u"cancel" in post_keys:
            return redirect("/management")
            
    else:
        return redirect("/")



def login_view(request):
    error = ""
    if request.method == 'POST': # If the form has been submitted...
        form = loginForm(request.POST) # A form bound to the POST data
        post_keys = request.POST.keys()
        logging.info(form)
        logging.info(request.POST)

        logging.info("retries=%d" % request.session["login_retries"])
        if request.session["login_retries"] > APP_LOGIN_MAX_RETRY:
            login_id = request.POST['login_id'].upper()
            try:
                user = User.objects.get(username=login_id)
                if user:
                    user.is_active = False
                    user.save()
            except:
                pass
            
            request.session["login_retries"] = 0

            return render_to_response('home.html', {'form':loginForm(), 'admin_email': APP_ADMIN_EMAIL, 'error':u"登入錯誤過多，帳號已被鎖定，請洽管理員。"}, context_instance=RequestContext(request))

        if u"signin" in post_keys:
            if form.is_valid(): # All validation rules pass
                login_id = request.POST['login_id'].upper()
                login_pw = request.POST['login_pw']

                user = authenticate(username=login_id, password=login_pw)

                if user is not None:
                    if user.is_active:
                        logging.info(user)
                        request.session["login_retries"] = 0
                        q_user = ntulgUser.objects.filter(id_number=login_id)[0]
                        #q_form = ntulgUserForm(instance=q_user)
                        request.session["q_user"] = q_user
                        return render_to_response('management.html', context_instance=RequestContext(request))
                    else:
                        error = u"帳號已被鎖定，請洽管理員。"
                else:
                    request.session["login_retries"] += 1
                    error = u"帳號或密碼錯誤"
            else:
                request.session["login_retries"] += 1
                error = u"帳號或密碼錯誤"
    else:
        form = loginForm() # An unbound form
        request.session["login_retries"] = 0#APP_PASSWORD_MAX_RETRY

    return render(request, 'home.html', {
        'form': form,
        'admin_email': APP_ADMIN_EMAIL,
        'error': error})
