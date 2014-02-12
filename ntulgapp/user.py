# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from ntulgapp.iso_country_codes import COUNTRY
from django.forms import ModelForm
from django.core.validators import RegexValidator
from django.core.validators import MinLengthValidator
from django.core.validators import MaxLengthValidator
from django import forms

INPUT_MAX = 50
MOBILE_LEN = 10

class ntulgUser(models.Model):
    user = models.OneToOneField(User)
    name_cht = models.CharField(verbose_name=u"中文姓名(chinese name)", max_length=INPUT_MAX) 
    name_eng = models.CharField(verbose_name=u"英文姓名(english name)", max_length=INPUT_MAX, help_text=u"格式:LI,DAFA(李,大發)(姓放前面,然後逗點,然後名)(不要使用\'-\'當分隔符號) <a href=\"http://www.englishname.org/\" target=\"_blank\">姓名英譯查詢</a>", validators=[RegexValidator(r'^[a-zA-Z ]+,[a-zA-Z ]+$')]) 
    birthday = models.DateField(verbose_name=u"生日(birthday)",max_length=10, help_text="格式:西元年-月-日,例如:1980-2-28(format: year-month-day)")
    tel_mobile= models.CharField(verbose_name=u"手機號碼(mobile)", help_text=u"不要輸入數字以外的符號",max_length=MOBILE_LEN, validators=[RegexValidator(r'^09[0-9]{8}$'),MinLengthValidator(MOBILE_LEN),MaxLengthValidator(MOBILE_LEN)])#, min_length=10)
    tel = models.CharField(verbose_name=u"電話(tel no.)", blank=True, max_length=INPUT_MAX, help_text=u"格式:(xx)xxxxxxxxx, 非必填(not required)", validators=[RegexValidator(r'^\(?[0-9]*\)\s*[0-9]*$'),MinLengthValidator(8),MaxLengthValidator(14)]) 
    email = models.EmailField(verbose_name=u"Email", max_length=INPUT_MAX)
    address = models.CharField(verbose_name=u"通訊地址(address)", help_text=u"請加上五碼郵遞區號(don't forget the ZIP code)", max_length=INPUT_MAX)
    nationality = models.CharField(verbose_name=u"國籍(nationality)", choices=COUNTRY.items(), default="TW", max_length=INPUT_MAX)
    identify_number = models.CharField(verbose_name=u"身份證字號(id)", help_text=u"外籍人士請填居留證號碼(if you..)", max_length=INPUT_MAX, validators=[RegexValidator(r'(^[a-zA-Z][12][0-9]{8}$|^[a-zA-Z][cCdD][0-9]{8}$)'),MinLengthValidator(10),MaxLengthValidator(10)])
    sex = models.CharField(verbose_name="性別(sex)", choices=(
        ("male",u"男(male)"),
        ("female",u"女(female)")
        ),max_length=INPUT_MAX, blank=True, help_text=u"非必填(not required)")
    if_still_ntu = models.CharField(verbose_name=u"現在是否為台大在校生(if you're now a NTU student)", choices=(("yes","是(yes)"),("no","否(no)")),max_length=INPUT_MAX)

    tshirt_size = models.CharField(verbose_name=u"t-shirt尺寸(size)", max_length=INPUT_MAX, choices=(("S","S"),("M","M"), ("L","L"),("XL","XL"),("2XL","2XL"),("3XL","3XL")), help_text=u"<a href=\"http://www.mit-clothes.com.tw/info/size.html\" target=\"_blank\">尺寸表(size chart)</a>")
    ptt_id = models.CharField(verbose_name=u"PTT ID",max_length=INPUT_MAX, blank=True, help_text=u"非必填(not required)")
    ptt2_id = models.CharField(verbose_name=u"PTT2 ID",max_length=INPUT_MAX,blank=True, help_text=u"非必填(not required)")

    if_vegetarian = models.CharField(verbose_name=u"是否吃素(vegetarian)", choices=(("yes","是(yes)"),("no","否(no)")),max_length=INPUT_MAX )    

    emergency_contact_name = models.CharField(verbose_name=u"緊急聯絡人姓名(emergency contact)", max_length=INPUT_MAX)
    emergency_contact_mobile = models.CharField(verbose_name=u"緊急聯絡人手機(emergency contact's mobile)", max_length=MOBILE_LEN, help_text=u"不要輸入數字以外的符號", validators=[RegexValidator(r'^09[0-9]{8}$'),MinLengthValidator(MOBILE_LEN),MaxLengthValidator(MOBILE_LEN)])


    beneficiary = models.CharField(verbose_name=u"保險受益人(beneficiary)",max_length=INPUT_MAX) 
    beneficiary_relationship = models.CharField(verbose_name=u"與保險受益人之關係(relationship to beneficiary)",max_length=INPUT_MAX)
    height = models.DecimalField(verbose_name=u"身高(height)", max_digits=3, help_text="cm")
    weight = models.DecimalField(verbose_name=u"體重(weight)", max_digits=3, help_text="kg")
    disease= models.CharField(verbose_name=u"特殊疾病(specified disease)", max_length=INPUT_MAX, blank=True, help_text=u"任何會妨礙訓練的疾病, 非必填(not required)") 


    source = models.CharField(verbose_name=u"如何得知本訓練(...)", max_length=INPUT_MAX)

    comment = models.TextField(verbose_name=u"建議/發問(comment)", max_length=INPUT_MAX,blank=True, help_text=u"非必填(not required)")

    facebook_id = models.CharField(verbose_name=u"Facebook ID", max_length=INPUT_MAX,blank=True, help_text=u"全為數字,非必填(all numbers, not required), <a href=\"http://findmyfacebookid.com\" target=\"_blank\">找ID(Help)</a>", validators=[RegexValidator(r'[0-9]'),MinLengthValidator(6),MaxLengthValidator(20)])  


class ntulgUserForm(ModelForm):
    class Meta:
        model = ntulgUser
        fields = [
                'name_cht',
                'name_eng',
                'nationality',
                'identify_number',
                'birthday',
                'sex',
                'tel_mobile',
                'tel',
                'email',
                'address',
                'height',
                'weight',
                'tshirt_size',
                'if_still_ntu',
                'if_vegetarian',
                'emergency_contact_name',
                'emergency_contact_mobile',
                'beneficiary',
                'beneficiary_relationship',
                'disease',
                'source',
                'comment',
                'facebook_id',
                'ptt_id',
                'ptt2_id',
                ]
        widgets = { 'address': forms.TextInput(attrs={'size': 80})}
