# _*_ coding: utf-8 _*_

from django import forms
from django.contrib.auth.models import User
from django.core.validators import validate_email, RegexValidator
from farmConnect.models import *#ProduceCategory,Produce, Demands, Orders,Bids
from django.utils.translation import ugettext_lazy as _
from datetimewidget.widgets import DateTimeWidget
from datetime import datetime, date
from time import localtime, strftime,mktime
from django.utils import timezone

import calendar
from django.conf import settings

class LocationForm(forms.Form):
    latitude = forms.CharField(max_length=6, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':_('Latitude')}) ,validators=[RegexValidator(r'^[0-9.]*$',message=_('Value should be a Co-ordinate'))])
    longitude = forms.CharField(max_length=6, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':_('Longitude')}) ,validators=[RegexValidator(r'^[0-9.]*$',message=_('Value should be a Co-ordinate'))])
    def clean(self):
        print "hi"
        cleaned_data = super(LocationForm, self).clean()
        print "boop"
        print cleaned_data
        return cleaned_data

class FarmForm(forms.Form):
    name = forms.CharField(max_length=160, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':_('Farm Name')}), )
    def clean(self):
        print "hi"
        cleaned_data = super(FarmForm, self).clean()
        print "boop"
        print cleaned_data
        return cleaned_data

class StoreForm(forms.Form):
    name = forms.CharField(max_length=160, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':_('Store Name')}), )
    def clean(self):
        print "hi"
        cleaned_data = super(StoreForm, self).clean()
        print "boop"
        print cleaned_data
        return cleaned_data
     
class AddressForm(forms.Form):
    door_no = forms.CharField(max_length = 6, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':_('Door Number')}),validators=[RegexValidator(r'^[0-9a-zA-Z\\/]*$',message=_('Enter only letters, numbers and \ , /'))])
    street = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':_('Street Name')}), )
    village = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':_('Village Name (or) Region')}), )
    town = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':_('Town Name (or) Taluk')}), )
    city = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':_('City (or) District')}), )
    STATE =( 
        ('AN',_('Andaman and Nicobar Islands')),
        ('AP',_('Andhra Pradesh')),
        ('AR',_('Arunachal Pradesh')),
        ('AS',_('Assam')),
        ('BR',_('Bihar')),
        ('CG',_('Chhattisgarh')),
        ('CH',_('Chandigarh')),
        ('DD',_('Daman and Diu')),
        ('DH',_('Dadra and Nagar Haveli')),
        ('DL',_('Delhi')),
        ('GA',_('Goa')),
        ('GJ',_('Gujarat')),
        ('HR',_('Haryana')),
        ('HP',_('Himachal Pradesh')),
        ('JK',_('Jammu and Kashmir')),
        ('JH',_('Jharkhand')),
        ('KA',_('Karnataka')),
        ('KL',_('Kerala')),
        ('LD',_('Lakshadweep')),
        ('MP',_('Madhya Pradesh')),
        ('MH',_('Maharashtra')),
        ('MN',_('Manipur')),
        ('ML',_('Meghalaya')),
        ('MZ',_('Mizoram')),
        ('NL',_('Nagaland')),
        ('OR',_('Orissa')),
        ('PB',_('Punjab')),
        ('PY',_('Pondicherry')),
        ('RJ',_('Rajasthan')),
        ('SK',_('Sikkim')),
        ('TN',_('Tamil Nadu')),
        ('TR',_('Tripura')),
        ('UK',_('Uttarakhand')),
        ('UP',_('Uttar Pradesh')),
        ('WB',_('West Bengal')),
    )

    state = forms.ChoiceField(choices=STATE, widget=forms.Select(attrs={'class':'form-control' }))
    pincode = forms.CharField(max_length=6, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':_('PIN Code')}) ,validators=[RegexValidator(r'^[0-9]*$',message=_('Enter only numbers'))])
    

    def clean(self):
        cleaned_data = super(AddressForm, self).clean()
        return cleaned_data

class RegistrationForm(forms.Form):
    user_types = (('1',_('Farmer'),),('2',_('Retailer'),))
    user_type = forms.ChoiceField(widget=forms.RadioSelect(attrs={'class': 'radios'}), choices=user_types)
    username = forms.CharField(max_length=20, label='Username: ',widget=forms.TextInput(attrs={'class':'form-control','placeholder':_('Username')}),validators=[RegexValidator(r'^[0-9a-zA-Z]*$',message=_('Enter only letters and numbers'))])
    firstname = forms.CharField(max_length = 40, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':_('First name')}), )
    lastname = forms.CharField(max_length = 80, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':_('Last name')}), )
    password1 = forms.CharField(max_length = 50, widget = forms.PasswordInput(attrs={'class':'form-control', 'placeholder': _('Password')}),)
    password2 = forms.CharField(max_length = 50, widget = forms.PasswordInput(attrs={'class':'form-control', 'placeholder': _('Confirm password')}),)
    email = forms.EmailField(max_length = 40, validators = [validate_email], widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':_('aa@bb.com')}),)
    #state = forms.ChoiceField(choices=STATE, widget=forms.Select(attrs={'class':'form-control', }))
    phone = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':_('Phone Number')}),validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$',message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."))])
    LANG = [
        ('en',_('English')),
        ('ta',_('Tamil')),
    ]
    language = forms.ChoiceField(choices=LANG, widget=forms.Select(attrs={'class':'form-control'}))
    
    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("Passwords did not match."))
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError(_("Username is already taken."))
        phone = cleaned_data.get('phone')
        
        return cleaned_data
        
    def clean_user_type(self):
        userType = self.cleaned_data.get('user_type')
        if not userType:
            raise forms.ValidationError(_("Choose an Account type"))
        return userType

        

class ProduceCategoryForm (forms.Form):
    name = forms.CharField(max_length=15) # ask TA?
    pic = forms.ImageField(required=False, 
                            label=_('Category Picture'),
                            widget = forms.FileInput())
    def clean(self):
        print "hi"
        cleaned_data = super(ProduceCategoryForm, self).clean()
        print "boop"
        print cleaned_data
        return cleaned_data
    def clean_pic(self):
        print 'clean_picture:'
        picture = self.cleaned_data['pic']
        print 'clean_picture:', picture
        if not picture:
            print "not a picture"
            return None
        #if not picture.content_type or not picture.content_type.startswith('image'):
        #    raise forms.ValidationError('File type is not image')
        #if picture.size > MAX_UPLOAD_SIZE:
        #    raise forms.ValidationError('File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
        return picture

class ProduceForm(forms.Form):
    name = forms.CharField(max_length=15) # ask TA?
    pic = forms.ImageField(required=False, 
                            label=_('Produce Picture'),
                            widget = forms.FileInput())
    def clean(self):
        print "hi"
        cleaned_data = super(ProduceForm, self).clean()
        print "boop"
        print cleaned_data
        return cleaned_data
    def clean_pic(self):
        print 'clean_picture:'
        picture = self.cleaned_data['pic']
        print 'clean_picture:', picture
        if not picture:
            print "not a picture"
            return None
        #if not picture.content_type or not picture.content_type.startswith('image'):
        #    raise forms.ValidationError('File type is not image')
        #if picture.size > MAX_UPLOAD_SIZE:
        #    raise forms.ValidationError('File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
        return picture

class DemandsForm(forms.Form):
    quantity = forms.IntegerField(min_value=1)
    price = forms.IntegerField(min_value=1)
    deldatetime = forms.DateTimeField(widget=DateTimeWidget(usel10n=True, bootstrap_version=3))
    biddatetime = forms.DateTimeField(widget=DateTimeWidget(usel10n=True, bootstrap_version=3))#forms.DateTimeField(input_formats = ['%m/%d/%Y, %H:%M %p',])
    def clean(self):
        cleaned_data = super(DemandsForm, self).clean()
        return cleaned_data

    def clean_deldatetime(self):
        deldatetime = self.cleaned_data.get('deldatetime')
        #print deldatetime
        #print timezone.now()
        currentTime = timezone.make_aware(datetime.now(),timezone.get_default_timezone())
        if(deldatetime<currentTime):
            raise forms.ValidationError(_("Delivery Date and time should should be greater than the current date and time"))
        return deldatetime
    def clean_biddatetime(self):
        biddateTime = self.cleaned_data.get('biddatetime')
        deldatetime = self.cleaned_data.get('deldatetime')
        print deldatetime
        if(biddateTime>=deldatetime):
            raise forms.ValidationError(_("Bid Date and time should should be lesser than the Delivery date and time"))
        return biddateTime

class BidsForm(forms.Form):

    pickup_datetime = forms.DateTimeField(widget=DateTimeWidget(usel10n=True, bootstrap_version=3))
    confirmation_datetime = forms.DateTimeField(widget=DateTimeWidget(usel10n=True, bootstrap_version=3))
    def clean(self):
        print "hi"
        cleaned_data = super(BidsForm, self).clean()
        print "boop"
        print cleaned_data
        return cleaned_data

class OrdersForm(forms.Form):
    ORDER_STATUS =(
        ("1", "Buyer unpaid"),
        ("2", "Buyer paid"),
        ("3", "Ready for shipment"),
        ("4","In transit"),
        ("5","Delivered"),
    )
    order_status = forms.ChoiceField(choices = ORDER_STATUS)