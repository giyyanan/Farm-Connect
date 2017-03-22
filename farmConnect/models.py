# -*- coding: utf-8 -*-
from django.db import models

# User class for built-in authentication module
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField

import pytz
#from easymode.i18n.decorators import I18n
#from django.utils import tzinfo

class Address(models.Model):
	door_no = models.CharField(max_length=6,blank=True)
	street = models.CharField(max_length=50,blank=True)
	village = models.CharField(max_length=50)
	town = models.CharField(max_length=50)
	city = models.CharField(max_length=50)
	state = models.CharField(default="", max_length=20, blank=True)
	pincode = models.DecimalField(max_digits=6,decimal_places=0)
	
	def __unicode__(self):
		return str(self.door_no+","+self.street+","+self.village+","+self.town+","+self.city+","+self.state+","+str(self.pincode))

	def __str__(self):
		return self.__unicode__()

class UserProfile(models.Model):
	user = models.OneToOneField(User)
	address = models.OneToOneField(Address, null=True, blank=True)
	language = models.CharField(default="en", max_length=3)
	phone = PhoneNumberField() #    fax_number = PhoneNumberField(blank=True)
	user_type = models.CharField(max_length=1,blank=True)


class ProduceCategory(models.Model):
	name = models.CharField(max_length=15)
	pic = models.FileField(upload_to="category_pictures",null=True,default="category_pictures/empty.png",)


class Produce(models.Model):
	name = models.CharField(max_length=15)
	category = models.ForeignKey(ProduceCategory)
	pic = models.FileField(upload_to="produce_pictures",null=True,default="produce_pictures/empty.png",)


class Location(models.Model):
	latitude = models.DecimalField(max_digits=8, decimal_places=3)
	longitude = models.DecimalField(max_digits=8, decimal_places=3)

class FarmProfile(models.Model):
	name = models.CharField(max_length=160)
	address = models.OneToOneField(Address)
	location = models.OneToOneField(Location)
	user  = models.ForeignKey(User)

class StoreProfile(models.Model):
	name = models.CharField(max_length=160)
	address = models.OneToOneField(Address)
	location = models.OneToOneField(Location)
	user  = models.ForeignKey(User)

class Demands(models.Model):
	buyer = models.ForeignKey(User) #models.ForeignKey(StoreProfile)
	quantity = models.PositiveIntegerField()
	price = models.PositiveIntegerField()
	delivery_datetime = models.DateTimeField()
	bid_end_datetime = models.DateTimeField()
	produce = models.ForeignKey(Produce)
	datetime = models.DateTimeField(auto_now=True)

	def getBidCount(self):
		return Bids.objects.filter(demand=self).count()

class Bids(models.Model):
	seller =  models.ForeignKey(User)
	pickup_datetime = models.DateTimeField()
	confirmation_datetime = models.DateTimeField()
	datetime = models.DateTimeField(auto_now=True)
	demand = models.ForeignKey(Demands)
	status = models.CharField(max_length=1) #??

	def rejectOtherBids(self):
		Bids.objects.filter(demand=self.demand).exclude(id=self.id).update(status='9')

class Orders(models.Model):
	bid = models.OneToOneField(Bids)
	#pickup_datetime = models.DateTimeField()
	datetime = models.DateTimeField(auto_now=True)
	status = models.CharField(max_length=1)


class TransportLogs(models.Model):
	location = models.ForeignKey(Location)
	datetime = models.DateTimeField(auto_now=True)
	log = models.CharField(max_length=300)
	order = models.ForeignKey(Orders)

class SupportedLanguages(models.Model):
	language_name = models.CharField(max_length=40)
	language_iso_code = models.CharField(max_length=3)
	iso_format = models.CharField(max_length=8)

