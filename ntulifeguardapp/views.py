# -*- coding: utf-8 -*-
import re
import pprint
from datetime import datetime, timedelta
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
from ntulifeguardapp.user import ntulgOldUserForm
from ntulifeguardapp.user import ntulgNewUserForm
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

BACK_TO_SYSTEM = u"<p><p><a href=\"/\">回到系統(back to the system)</a>"

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
    #post.pop("cap_no")

    now = datetime.now() + timedelta(hours=8)
    post["date-added"] = now.strftime("%Y/%m/%d %H:%M:%S")
 
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

def make_password():
    return ''.join(random.choice(string.ascii_letters + string.digits + string.punctuation) for x in range(12))

def create_user(user_title, user_name, email):
    #password = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(8))
    password = make_password()
    logging.info("user_name=%s, password=%s" % (user_name, password))
    
    try:
        User.objects.get(username=user_name)

    except User.DoesNotExist:
        user = User.objects.create_user(user_name, email, password)

        if user:
            user.save()

            body = u"%s 你好，\n你的密碼如下：\n%s\n\n請由此登入管理系統：%s" % (user_title, password, APP_URL)

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
    old_pw = forms.CharField(required=False, label=u'舊密碼(old password)', max_length=USER_INPUT_LEN_MAX, widget=forms.PasswordInput)
    new_pw = forms.CharField(required=False, label=u'新密碼(new password)', max_length=USER_INPUT_LEN_MAX)
    new_pw_confirm = forms.CharField(required=False, label=u'再次輸入新密碼(new password again)', max_length=USER_INPUT_LEN_MAX)

class loginForm(forms.Form):
    login_id = forms.CharField(required=False, label=u'帳號(account)', help_text=u'你的身分證字號/居留證號碼(your ID.)', max_length=10)
    login_pw = forms.CharField(required=False, label=u'密碼(password)', max_length=USER_INPUT_LEN_MAX, widget=forms.PasswordInput)

# used after copy()
def trim_leading_zeros(post):
    keys = ["stage_no", "cap_no", "height", "weight"]

    for k in keys:
        if post.get(k):
            post[k] = post[k].lstrip("0")

def signup_view(request, if_training):

    if request.method == 'POST': # If the form has been submitted...
        logging.info(request.POST)
        new_post = request.POST.copy()
        trim_leading_zeros(new_post)

        new_post["id_number"] = new_post.get("id_number").upper()
        
        if if_training:
            new_post["stage_no"] = str(CURRENT_STAGE["no"])

            form = ntulgNewUserForm(new_post) # A form bound to the POST data
            form.fields['stage_no'].widget = forms.HiddenInput()
        else:
            form = ntulgOldUserForm(new_post)

        post_keys = request.POST.keys()

        if u"confirm" in post_keys:
            if form.is_valid(): # All validation rules pass
                user = create_user(new_post['name_cht'], new_post['id_number'], new_post['email'])
                if user is not None:
                    n = form.save()
                    if if_training:
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
        if if_training:
            form = ntulgNewUserForm() # An unbound form
            form.fields['stage_no'].widget = forms.HiddenInput()
        else:
            form = ntulgOldUserForm()

        return render_to_response('signup.html',{
            'form':form,
            'uploader_url':APP_IMG_UPLOADER_URL,
            'if_training':if_training
            },context_instance=RequestContext(request))

def management_view(request):
    logging.info("management_view")
    
    ntu_user = request.session.get("ntu_user")

    #logging.info(ntu_user)
    post_keys = request.POST.keys()

    if ntu_user is not None: # If the form has been submitted...
        logging.info(ntu_user.id)
        logging.info(ntu_user.id_number)

        if u"update_data" in post_keys:
            form = ntulgUserUpdateForm(instance=ntu_user)
            #form = ntulgNewUserForm(instance=ntu_user)
            return render_to_response('update_data.html', {
            'uploader_url':APP_IMG_UPLOADER_URL+ntu_user.id_number,
            'form':form}, context_instance=RequestContext(request))

        elif u"update_password" in post_keys:
            form = updatePasswordForm()
            return render_to_response('update_password.html', {'form':form}, context_instance=RequestContext(request))
        elif u"cancel_training" in post_keys:
            return render_to_response('cancel.html', {'ntu_user':ntu_user}, context_instance=RequestContext(request))
        elif u"cancel_account" in post_keys:
            return render_to_response('cancel.html', {'ntu_user':ntu_user}, context_instance=RequestContext(request))
        elif u"logout" in post_keys:
            request.session.flush()
            return redirect("/")
        else: 
            return render_to_response('management.html', {'ntu_user':ntu_user}, context_instance=RequestContext(request))
    else:
        return redirect("/")

class forgetPasswordForm(forms.Form):
    login_id = forms.CharField(required=False, label=u'帳號(account)', help_text=u'你的身分證字號/居留證號碼(your ID.)', max_length=10)
    email = forms.CharField(required=False, label=u'當初註冊的email(your registered email)', max_length=USER_INPUT_LEN_MAX)
    #birthday = forms.DateField(required=False, label=u'你的生日(birthday)', help_text=u'格式：西元年-月份-日，如1990-2-2。(your birthday, format: year-month-day, ex: 1990-2-2)')

def forget_password_view(request):

    logging.info("forget_password_view")
    
    post_keys = request.POST.keys()

    if request.method == 'POST': # If the form has been submitted...
        if u"confirm" in post_keys:
            try: 
                user = User.objects.get(idxf_email_l_iexact=request.POST['email'].lower(), idxf_username_l_iexact=request.POST['login_id'].lower(), is_active=True)
            except:
                return HttpResponse(u"使用者不存在，請聯絡管理員。%s" % BACK_TO_SYSTEM)
            else:
                try:
                    new_password = make_password()
                    logging.info("new_password=%s" % new_password)
                    user.set_password(new_password)
                    user.save()

                    body = u"你好，\n你的新密碼如下：\n%s\n\n請由此登入管理系統：%s" % (new_password, APP_URL)

                    try:
                        mail.send_mail(sender=APP_ADMIN_EMAIL,to=user.email, subject=APP_EMAIL_GREETING, body=body)
                    except:
                        pass


                except:
                    return HttpResponse(u"系統錯誤，請聯絡管理員。%s" % BACK_TO_SYSTEM)
                else:
                    return HttpResponse(u"新密碼已經寄到你的email，請收信。%s" % BACK_TO_SYSTEM)
        else:
            return redirect("/")
    else:
        form = forgetPasswordForm()
        return render_to_response('forget_password.html', {'form':form, 'info': u"新密碼將會寄到你的email"}, context_instance=RequestContext(request))




def cancel_view(request):

    ntu_user = request.session.get("ntu_user")
    auth_user = request.session.get("auth_user")

    post_keys = request.POST.keys()

    if ntu_user is not None: # If the form has been submitted...
        if u"yes" in post_keys:
            try:
                ntu_user.delete()
                auth_user.delete()
            except:
                pass

            request.session.flush()

            return HttpResponse("帳號已經移除，謝謝使用本系統。(Your account has been removed.)<p><p><a href=\"/\">回到系統(back to the system)</a>")

        elif u"no" in post_keys:
            return render_to_response('management.html', {'ntu_user':ntu_user}, context_instance=RequestContext(request))
        else:
            return redirect("/")
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
    ntu_user = request.session.get("ntu_user")
    if request.method == 'POST': # If the form has been submitted...
       
        post_keys = request.POST.keys()
        if u"confirm" in post_keys:
            form = updatePasswordForm(request.POST)

            old_pw = request.POST.get(u'old_pw')
            new_pw = request.POST.get(u'new_pw')
            new_pw_confirm = request.POST.get(u'new_pw_confirm')

            user = authenticate(username=ntu_user.id_number, password=old_pw)

            if user is not None and user.is_active:
                if new_pw == new_pw_confirm:
                    if check_new_password(old_pw, new_pw):
                        user.set_password(new_pw)
                        user.save()
                        return render_to_response('management.html',{'info':u"密碼更新成功", 'ntu_user':ntu_user},context_instance=RequestContext(request))
                    else:
                        return render_to_response('update_password.html', {'form': form, 'error':u"新密碼不符合規則，請重新輸入。"}, context_instance=RequestContext(request))

                else:
                    return render_to_response('update_password.html', {'form': form, 'error':u"兩組新密碼不一致"}, context_instance=RequestContext(request))

            else:
                return render_to_response('update_password.html', {'form':form, 'error':u"舊密碼錯誤，請檢查"}, context_instance=RequestContext(request))

        elif u"cancel" in post_keys:
            return render_to_response('management.html',{'ntu_user':ntu_user},context_instance=RequestContext(request))
            #return render_to_response('management.html',{'if_training': True if ntu_user.stage_no == str(CURRENT_STAGE.get("no")) else False},context_instance=RequestContext(request))
            #return redirect("/management")
            
    else:
        return redirect("/")


def update_data_view(request):
    if request.method == 'POST': # If the form has been submitted...
        new_post = request.POST.copy()
        trim_leading_zeros(new_post)
        post_keys = request.POST.keys()
        ntu_user = request.session.get("ntu_user")

        if ntu_user is None:
            return redirect("/")

        form = ntulgUserUpdateForm(new_post, instance=ntu_user)
        
        if u"confirm" in post_keys:
            if form.is_valid():
                logging.info("confirm update")

                form.save()
                request.session["ntu_user"] = form.save()

                #FIXME: as should shave only one email field in model
                auth_user = request.session.get("auth_user")
                if ntu_user.email != auth_user.email:
                    auth_user.email = ntu_user.email
                    auth_user.save()

                return render_to_response('management.html',{'info':u"資料更新成功", 'ntu_user':ntu_user},context_instance=RequestContext(request))
            else:
                return render_to_response('update_data.html', {'form':form, 'error':u"表單錯誤請檢查"}, context_instance=RequestContext(request))

        elif u"cancel" in post_keys:
            return render_to_response('management.html',{'ntu_user':ntu_user},context_instance=RequestContext(request))
            
    else:
        return redirect("/")



def login_view(request):
    error = ""
    if request.method == 'POST': # If the form has been submitted...
        form = loginForm(request.POST) # A form bound to the POST data
        post_keys = request.POST.keys()
        logging.info(form)
        logging.info(request.POST)

        logging.info("retries=%d" % request.session.get("login_retries"))
        if request.session.get("login_retries") > APP_LOGIN_MAX_RETRY:
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

                request.session["auth_user"] = user

                if user is not None:
                    if user.is_active:
                        logging.info(user)
                        request.session["login_retries"] = 0
                        try:
                            ntu_user = ntulgUser.objects.get(id_number=login_id)
                        except:
                            # not really..
                            error = u"帳號已被鎖定，請洽管理員。"
                            pass
                        else:
                            request.session["ntu_user"] = ntu_user
                            request.session["ntu_user"].current_stage = CURRENT_STAGE
                            request.session["ntu_user"].if_training = True if ntu_user.stage_no == str(CURRENT_STAGE.get("no")) else False 
                            return render_to_response('management.html',{'info':u"%s 你好，歡迎登入系統。" % ntu_user.name_cht, 'ntu_user': ntu_user}, context_instance=RequestContext(request))
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
        request.session["login_retries"] = 0 #APP_PASSWORD_MAX_RETRY

    return render(request, 'home.html', {
        'form': form,
        'admin_email': APP_ADMIN_EMAIL,
        'error': error})
