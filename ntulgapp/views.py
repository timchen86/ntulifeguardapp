# -*- coding: utf-8 -*-
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
from ntulgapp.user import ntulgUser
from ntulgapp.user import ntulgUserForm
from ntulgapp.user import ntulgUserUpdateForm
from ntulgapp.globals import CURRENT_STAGE
from ntulgapp.globals import APP_URL
from ntulgapp.globals import APP_ADMIN_EMAIL
from ntulgapp.globals import APP_NOTICE_EMAIL
from django.contrib.auth.models import User
import string
import random
from google.appengine.api import mail
from django.shortcuts import redirect

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
    #new_post_data['identify_number']= u"K123123123"
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

def send_notice(post):
    stage_no=CURRENT_STAGE.get("no")
    current_stage_count = ntulgUser.objects.filter(stage_no=stage_no).count()
    subject = u"%s期 第%d名報名者" % (stage_no,current_stage_count)
    
    post.pop("csrfmiddlewaretoken")
    post.pop("confirm")
    body = ""
    for k,v in post.iteritems():
        body = body+"%s: %s"%(k,v)+"\n"

    logging.info(subject)
    logging.info(body)
    try:
        mail.send_mail(sender=APP_ADMIN_EMAIL, to=APP_NOTICE_EMAIL, subject=subject, body=body)
    except:
        pass

def create_user(user_title, user_name, email):
    password = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(8))
    logging.info("user_name=%s, password=%s" % (user_name, password))

    if User.objects.filter(username=user_name).count():
        return None

    user = User.objects.create_user(user_name, email, password)
    user.save()
    body = u"%s 你好，\n你的密碼是：%s\n\n請由此登入管理系統：%s" % (user_title, password, APP_URL)
    #admin_user_email = appengine_users.get_current_user().email()
    try:
        mail.send_mail(sender=APP_ADMIN_EMAIL,to=email,subject=u"謝謝使用台大救生班隊員資料管理系統", body=body)
    except:
        pass
    return user

class updatePasswordForm(forms.Form):
    old_pw = forms.CharField(required=False, label=u'舊密碼(old password)', max_length=USER_INPUT_LEN_MAX)
    new_pw = forms.CharField(required=False, label=u'新密碼(new password)', max_length=USER_INPUT_LEN_MAX)
    new_pw_confirm = forms.CharField(required=False, label=u'再次輸入新密碼(new password again)', max_length=USER_INPUT_LEN_MAX)

class loginForm(forms.Form):
    login_id = forms.CharField(required=False, label=u'帳號(account)', help_text=u'你的身分證字號/居留證號碼(your ID.)', max_length=USER_INPUT_LEN_MAX)
    login_pw = forms.CharField(required=False, label=u'密碼(password)', max_length=USER_INPUT_LEN_MAX)
    #login_pw = forms.CharField(required=False, label=u'密碼(password)', max_length=USER_INPUT_LEN_MAX, widget=forms.PasswordInput)


def signup_view(request, if_training):

    if request.method == 'POST': # If the form has been submitted...
        new_post = request.POST.copy()
        new_post["identify_number"] = new_post.get("identify_number").upper()
        
        if if_training:
            new_post["stage_no"] = CURRENT_STAGE["no"]

        form = ntulgUserForm(new_post) # A form bound to the POST data
        if if_training:
            form.fields['stage_no'].widget = forms.HiddenInput()
            form.fields['cap_no'].widget = forms.HiddenInput()

        post_keys = request.POST.keys()

        if u"confirm" in post_keys:
            if form.is_valid(): # All validation rules pass
                user = create_user(new_post['name_cht'], new_post['identify_number'], new_post['email'])
                if user is not None:
                    n = form.save()
                    send_notice(new_post)
                    return render_to_response('signup_feedback.html', {'Email': new_post["email"]},context_instance=RequestContext(request) )
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
            'if_training':if_training
            },context_instance=RequestContext(request))

def management_view(request):
    logging.info("management_view")
    
    q_user = request.session.get("q_user")

    #logging.info(q_user)
    post_keys = request.POST.keys()

    if q_user is not None: # If the form has been submitted...
        logging.info(q_user.id)
        logging.info(q_user.identify_number)

        if u"update_data" in post_keys:
            form = ntulgUserUpdateForm(instance=q_user)
            #form = ntulgUserForm(instance=q_user)
            return render_to_response('update_data.html', {'form':form}, context_instance=RequestContext(request))

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

def update_password_view(request): #, user_name=None):
    q_user = request.session.get("q_user")
    logging.info(q_user)
    logging.info(dir(q_user))
    if request.method == 'POST': # If the form has been submitted...
       
        post_keys = request.POST.keys()
        if u"confirm" in post_keys:
            user = authenticate(username=q_user.identify_number, password=request.POST.get(u'old_pw'))

            if user is not None and user.is_active:
                #return render_to_response('update_data.html', {'form':q_form, 'error':u"表單錯誤請檢查"}, context_instance=RequestContext(request))
                new_pw = request.POST.get(u'new_pw')
                new_pw_confirm = request.POST.get(u'new_pw_confirm')
                if new_pw == new_pw_confirm:
                    user.set_password(new_pw)
                    user.save()
                    return render_to_response('management.html', {'info':u"密碼更新完成，請用新密碼登入系統"}, context_instance=RequestContext(request))
                else:
                    form = updatePasswordForm(request.POST)
                    return render_to_response('update_password.html', {'form': form, 'error':u"兩組新密碼不一致"}, context_instance=RequestContext(request))

            else:
                form = updatePasswordForm(request.POST)
                return render_to_response('update_password.html', {'form':form, 'error':u"舊密碼錯誤，請檢查"}, context_instance=RequestContext(request))

        elif u"cancel" in post_keys:
            return redirect("/management")
            
    else:
        return redirect("/")


def update_data_view(request):
    if request.method == 'POST': # If the form has been submitted...
        new_post = request.POST.copy()

        q_user_temp = ntulgUser.objects.filter(identify_number=new_post.get("identify_number"))
        if q_user_temp is not None:
            q_user = q_user_temp[0]
        else:
            return redirect("/")

        q_form = ntulgUserUpdateForm(new_post, instance=q_user)
        #q_form = ntulgUserForm(new_post, instance=q_user)

        logging.info(q_user.id)
        logging.info(q_user.identify_number)
        
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
        if u"signin" in post_keys:
            if form.is_valid(): # All validation rules pass
                login_id = request.POST['login_id'].upper()
                login_pw = request.POST['login_pw']

                user = authenticate(username=login_id, password=login_pw)

                if user is not None:
                    if user.is_active:
                        logging.info(user)
                        q_user = ntulgUser.objects.filter(identify_number=login_id)[0]
                        #q_form = ntulgUserForm(instance=q_user)
                        request.session["q_user"] = q_user
                        return render_to_response('management.html', context_instance=RequestContext(request))
                else:
                    error = u"帳號或密碼錯誤"
            else:
                error = u"帳號或密碼錯誤"

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
            'signup_training': True}

            return render_to_response('signup.html', param)

    else:
        form = loginForm() # An unbound form

    return render(request, 'home.html', {
        'form': form,
        'admin_email': APP_ADMIN_EMAIL,
        'error': error})
