# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from ntulifeguardapp.iso_country_codes import COUNTRY
from django.forms import ModelForm
from django.core.validators import RegexValidator
from django.core.validators import MinLengthValidator
from django.core.validators import MaxLengthValidator
from django import forms
import logging
from django.utils.six import with_metaclass

logger = logging.getLogger(__name__)
INPUT_MAX = 50
MOBILE_LEN = 10
PASSWORD_LEN = 200

class ntulgUser(models.Model):
    stage_no = models.DecimalField(max_digits=10, decimal_places=0, verbose_name=u"救生班期數(stage no.)", help_text=u"非水協期數") #, help_text="cm")
    cap_no = models.DecimalField(max_digits=3, decimal_places=0, verbose_name=u"泳帽號碼(cap no.)", blank=True, null=True, help_text=u"非必填(optional)")#, help_text="cm")
    name_cht = models.CharField(verbose_name=u"中文姓名(chinese name)", max_length=INPUT_MAX) 
    name_eng = models.CharField(verbose_name=u"英文姓名(english name)", max_length=INPUT_MAX, help_text=u"格式:LI, DAFA(李,大發)(姓放前面,然後逗點,然後名)(不要使用\'-\'當分隔符號) <a href=\"http://www.englishname.org/\" target=\"_blank\">姓名英譯查詢</a>", validators=[RegexValidator(r'^[a-zA-Z ]+,[a-zA-Z ]+$')]) 
    birthday = models.DateField(verbose_name=u"生日(birthday)",max_length=10, help_text="格式:西元年-月-日,例如:1980-2-28(format: year-month-day)")
    tel_mobile= models.CharField(verbose_name=u"手機號碼(mobile)", help_text=u"不要輸入數字以外的符號(don't enter anything other than numbers)",max_length=MOBILE_LEN, validators=[RegexValidator(r'^09[0-9]{8}$'),MinLengthValidator(MOBILE_LEN),MaxLengthValidator(MOBILE_LEN)])#, min_length=10)
    tel = models.CharField(verbose_name=u"電話(telephone no.)", blank=True, null=True,max_length=INPUT_MAX, help_text=u"格式:(xx)xxxxxxxxx, 非必填(optional)", validators=[RegexValidator(r'^\(?[0-9]*\)\s*[0-9]*$'),MinLengthValidator(8),MaxLengthValidator(14)]) 
    email = models.EmailField(verbose_name=u"Email", max_length=INPUT_MAX, help_text="請填寫正確，管理系統的密碼將會寄到這個Email")
    address = models.CharField(verbose_name=u"通訊地址(address)", help_text=u"請加上五碼郵遞區號(don't forget the ZIP code), <a href=\"http://www.moneymanager.url.tw/台灣3+2郵遞區號查詢系統.htm\" target=\"_blank\">查詢五碼郵遞區號</a>", max_length=INPUT_MAX)
    nationality = models.CharField(verbose_name=u"國籍(nationality)", choices=COUNTRY, default="TW", max_length=INPUT_MAX)
    id_number = models.CharField(verbose_name=u"身分證字號(ID.)", help_text=u"這將會是登入管理系統的帳號，外籍人士請填居留證號碼(this is your account name to login to the management system)", max_length=10, validators=[RegexValidator(r'(^[a-zA-Z][12][0-9]{8}$|^[a-zA-Z][cCdD][0-9]{8}$)'),MinLengthValidator(10),MaxLengthValidator(10)],unique=True)
    sex = models.CharField(verbose_name="性別(sex)", choices=(
        ("male",u"男(male)"),
        ("female",u"女(female)")
        ),max_length=INPUT_MAX, null=True,blank=True, help_text=u"非必填(optional)")
    occupation = models.CharField(verbose_name=u"職業(occupation)", max_length=INPUT_MAX)
    educational_background = models.CharField(verbose_name=u"學歷(educational background)", max_length=INPUT_MAX)
    if_present_ntu = models.BooleanField(verbose_name=u"現在是否為台大在校生(if you're now a NTU student)", default=None, choices=((None,"請選擇"),(True,"是(yes)"),(False,"否(no)")),max_length=INPUT_MAX)

    tshirt_size = models.CharField(verbose_name=u"t-shirt尺寸(size)", max_length=INPUT_MAX, default=None, choices=((None,u"請選擇"),("S","S"),("M","M"),("L","L"),("XL","XL"),("2XL","2XL"),("3XL","3XL")), help_text=u"<a href=\"http://www.mit-clothes.com.tw/info/size.html\" target=\"_blank\">尺寸表(size chart)</a>")
    ptt_id = models.CharField(verbose_name=u"PTT ID",max_length=INPUT_MAX, blank=True, help_text=u"非必填(optional)")
    ptt2_id = models.CharField(verbose_name=u"PTT2 ID",max_length=INPUT_MAX,blank=True, help_text=u"非必填(optional)")

    if_vegetarian = models.BooleanField(verbose_name=u"是否吃素(vegetarian)", default=None, choices=((None,"請選擇"),(True,"是(yes)"),(False,"否(no)")),max_length=INPUT_MAX )    

    emergency_contact = models.CharField(verbose_name=u"緊急聯絡人姓名(emergency contact)", max_length=INPUT_MAX)
    emergency_contact_mobile = models.CharField(verbose_name=u"緊急聯絡人手機(emergency contact's mobile)", max_length=MOBILE_LEN, help_text=u"不要輸入數字以外的符號(don't enter anything other than numbers)", validators=[RegexValidator(r'^09[0-9]{8}$'),MinLengthValidator(MOBILE_LEN),MaxLengthValidator(MOBILE_LEN)])


    beneficiary = models.CharField(verbose_name=u"保險受益人(beneficiary)",max_length=INPUT_MAX) 
    beneficiary_relationship = models.CharField(verbose_name=u"與保險受益人之關係(relationship to beneficiary)",max_length=INPUT_MAX)
    height = models.DecimalField(verbose_name=u"身高(height)", max_digits=3, decimal_places=0, help_text=u"cm, 非必填(optional)", null=True,blank=True)
    weight = models.DecimalField(verbose_name=u"體重(weight)", max_digits=3, decimal_places=0, help_text=u"kg, 非必填(optional)", null=True,blank=True)
    medical_history = models.CharField(verbose_name=u"特殊病史(medical history)", max_length=INPUT_MAX, help_text=u"任何會影響訓練的疾病, 沒有請填\"無\"。(medical history that should be consulted with a physician prior to engaging exercise or continuing to exercise)") 
    birthplace = models.CharField(verbose_name=u"出生地(birthplace)", max_length=INPUT_MAX) 

    choice_blood_types = ((None,"請選擇"),("A","A"),("B","B"),("AB","AB"),("O","O"))
    blood_type = models.CharField(choices=choice_blood_types, verbose_name=u"血型(blood type)", default=None, max_length=INPUT_MAX)

    source = models.CharField(verbose_name=u"如何得知本訓練(what brings you here)", max_length=INPUT_MAX)

    comment = models.TextField(verbose_name=u"建議/發問(comment)", max_length=INPUT_MAX,blank=True, null=True,help_text=u"非必填(optional)")

    facebook_id = models.CharField(verbose_name=u"Facebook ID", max_length=INPUT_MAX,blank=True, null=True,help_text=u"全為數字,非必填(all numbers, optional), <a href=\"http://findmyfacebookid.com\" target=\"_blank\">找ID(Help)</a>", validators=[RegexValidator(r'[0-9]'),MinLengthValidator(6),MaxLengthValidator(20)])  

    food_allergy = models.CharField(verbose_name=u"過敏的食物/藥物(food/drug allergy)", max_length=INPUT_MAX, help_text=u"沒有請填\"無\"")

    motivation = models.TextField(verbose_name=u"動機(motivation)", help_text=u"為何想參加台大救生班(why do you like to attend the training)", max_length=INPUT_MAX)

class ntulgUserForm(ModelForm):
    error_css_class = 'error'

    class Meta:
        model = ntulgUser
        fields = [
                'stage_no',
                'cap_no',
                'name_cht',
                'name_eng',
                'nationality',
                'id_number',
                'email',
                'birthday',
                'sex',
                'tel_mobile',
                'tel',
                'address',
                'height',
                'weight',
                'tshirt_size',
                'occupation',
                'educational_background',
                'if_present_ntu',
                'if_vegetarian',
                'birthplace',
                'emergency_contact',
                'emergency_contact_mobile',
                'beneficiary',
                'beneficiary_relationship',
                'medical_history',
                'food_allergy',
                'blood_type',
                'source',
                'motivation',
                'comment',
                'facebook_id',
                'ptt_id',
                'ptt2_id',
                ]
        widgets = { 
        'address': forms.TextInput(attrs={'size': 50}),
        }

class ntulgUserUpdateForm(ntulgUserForm):
    readonly_fields = ("id_number",)
    #ntulgUserForm.base_fields['id_number'].help_text = u"無法變更，如要變更請洽管理員"
