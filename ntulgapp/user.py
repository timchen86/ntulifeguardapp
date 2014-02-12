# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from ntulgapp.iso_country_codes import COUNTRY
from django.forms import ModelForm

class ntulgUser(models.Model):
    user = models.OneToOneField(User)
    name_cht = models.CharField() 
    name_eng = models.CharField() 
    birthday = models.DateField()
    tel_mobile= models.CharField()
    tel = models.CharField()
    address = models.CharField()
    nationality = models.CharField(choices=COUNTRY.items(), default="TW")
    identify_number = models.CharField()
    sex = models.CharField(choices=(
        ("male",u"男(male)"),
        ("female",u"女(female)"),
        ("unknown",u"未知(unknown)")))
    still_ntu = models.CharField(choices=(
        (True,u"是(still NTU student)"),
        (False,u"否(not NTU student)")))

    #email = models.EmailField()

    ptt_id = models.CharField()

    if_vegetarian = models.BooleanField()    
    #vegetarian 素食. ( ) non-vegetarian 葷食

    emergency_contact_name = models.CharField()
    emergency_contact_mobile = models.CharField()

    beneficiary_name = models.CharField() 
    beneficiary_relationship = models.CharField()
    sickness = models.CharField() 
    habbit = models.CharField()

    source = models.CharField()

    comment = models.TextField(max_length=100)

    facebook_id = models.CharField()  


class ntulgUserForm(ModelForm):
    class Meta:
        model = ntulgUser
        fields = [
                'name_cht',
                'name_eng',
                'birthday']
