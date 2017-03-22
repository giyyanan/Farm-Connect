from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from mimetypes import guess_type
from django.utils import translation

from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse,Http404
from django.core import serializers

from django.db import transaction
from farmConnect.forms import *
from farmConnect.models import *
from twilio.rest import TwilioRestClient
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings

@transaction.atomic
def register(request):
	context = {}
	try:
		if request.method =='GET':
			context['form']=RegistrationForm()
			return render(request, 'register.html', context)

		form = RegistrationForm(request.POST, request.FILES)
		context['form']=form
		if not form.is_valid():
			return render(request,'register.html', context)

		new_user = User.objects.create_user(username=form.cleaned_data['username'],
										password = form.cleaned_data['password1'],
										first_name = form.cleaned_data['firstname'],
										last_name = form.cleaned_data['lastname'],
										email = form.cleaned_data['email']
										)
		new_user.is_active = False
		new_user.save()
		#print User.objects.all()
		new_user_profile = UserProfile(user = new_user,
								   phone = form.cleaned_data['phone'],
								   user_type= form.cleaned_data['user_type'],
								   )
		#new_user_profile.is_active = False
		new_user_profile.save();
		#print(UserProfile.objects.all())
		context['phone_number'] = form.cleaned_data['phone'];
		token = default_token_generator.make_token(new_user)

		SMS_message = _("Welcome to Farm Connect .  Please click the link below to verify your phone number and complete the registration of your account:")+" http://%s%s" % (request.get_host(),reverse('confirm', args=(new_user.username, token)))

		client = TwilioRestClient(settings.SMS_ACC_SID, settings.SMS_AUTH_TOKEN)
		message = client.messages.create(body=SMS_message,to=form.cleaned_data['phone'],from_=settings.SMS_NUMBER)
		print context
		print "registration complete"
	except:
		context['form']=RegistrationForm()
		context['error'] = _('Error occured during registration')
		return render(request,'register.html', context)
	
	return render(request, 'confirmation.html', context)
		#return redirect(reverse('home'))

@login_required
def home(request):
	context = {}
	try:
		UserInfo = UserProfile.objects.get(user=request.user)
		context['User'] = UserInfo
		
		if not UserInfo.address:
			context['info'] = _('Address is not stored for user. Go to accounts to update the address')
		translation.activate(UserInfo.language)
	except:
		context['error'] = _('failed to fetch user information')
	return render(request, 'home.html', context)

@login_required
def sendSMS(request,number,message,context):
	try:
		client = TwilioRestClient(settings.SMS_ACC_SID, settings.SMS_AUTH_TOKEN)
		message = client.messages.create(body=message,to=number,from_=settings.SMS_NUMBER)
	except:
		context['error'] = _('failed to send SMS')
	return context
@login_required
def account(request):
	context = {}
	UserInfo = UserProfile.objects.get(user=request.user)
	try:
		context['User'] = UserInfo
	except:
		context['error'] = _('failed to fetch account details')	

	translation.activate(UserInfo.language)
	return render(request, 'account.html', context)

@login_required
@transaction.atomic
def profile(request):
	context = {}
	user = User.objects.get(username=request.user)
	UserInfo = UserProfile.objects.get(user=request.user)
	try:
		context['User'] = UserInfo
		context['UserAcc'] = user
		translation.activate(UserInfo.language)

		if request.method =='GET':
			context['form'] = RegistrationForm()
			return render(request, 'profile.html', context)
 
		form = RegistrationForm(request.POST,request.FILES)
		form.fields.pop('username')
		form.fields.pop('password1')
		form.fields.pop('password2')
		form.fields.pop('user_type')

		context['form'] = form
		print form

		if not form.is_valid():
			context['error'] = _('form is not valid')
			return render(request,'profile.html', context)
	
		#print form
		UserAcc = User.objects.select_for_update().get(username=request.user)

		UserAcc.first_name = form.cleaned_data['firstname']
		UserAcc.last_name = form.cleaned_data['lastname']
		UserAcc.email = form.cleaned_data['email']

		UserAcc.save()
		#print UserAcc.last_name

		User_info = UserProfile.objects.select_for_update().get(user=request.user)
		User_info.phone = form.cleaned_data['phone']
		User_info.language = form.cleaned_data['language']
		#print User_info.language
		User_info.save()
		context['User'] = User_info
		context['UserAcc'] = UserAcc
		context = sendSMS(request,str(User_info.phone),"Farm Connect : Your Profile Information has been modified",context)

		context['notify'] = _('User Information updated Successfully')
		
	except:
		context['error'] = _('failed to save profile')

	translation.activate(UserInfo.language)
	return render(request,'profile.html', context)

@login_required
@transaction.atomic
def stores(request):
	context ={}
	user = User.objects.get(username=request.user)
	UserInfo = UserProfile.objects.get(user=request.user)
	context['User'] = UserInfo
	try:
		if request.method =='GET':
			context['addressForm'] = AddressForm()
			context['storeForm'] = StoreForm()
			context['locationForm'] = LocationForm()
			return render(request, 'stores.html', context)

	
		addressForm = AddressForm(request.POST)
		print addressForm
		storeForm = StoreForm(request.POST)
		print storeForm
		locationForm = LocationForm(request.POST)
		if not addressForm.is_valid() or not storeForm.is_valid():
			context['addressForm'] = addressForm
			context['storeForm'] = storeForm
			context['locationForm'] = locationForm
			context['view'] = "errors"
			return render(request, 'stores.html', context)

		address = Address(door_no=addressForm.cleaned_data['door_no'],
										street = addressForm.cleaned_data['street'],
										village = addressForm.cleaned_data['village'],
										town = addressForm.cleaned_data['town'],
										city = addressForm.cleaned_data['city'],
										state = addressForm.cleaned_data['state'],
										pincode = addressForm.cleaned_data['pincode']
										)
		address.save()
		print address
		store = StoreProfile(name = storeForm.cleaned_data['name'],user = request.user,address=address)
		store.save()
	except:
		context['error'] = _('failed to fetch save stores')	

	translation.activate(UserInfo.language)
	return render(request, 'stores.html', context)

@login_required
@transaction.atomic
def address(request):
	context ={}
	user = User.objects.get(username=request.user)
	UserInfo = UserProfile.objects.get(user=request.user)
	context['User'] = UserInfo
	try:
		translation.activate(UserInfo.language)
		if request.method =='GET' and not UserInfo.address :
			context['form']=AddressForm()
			return render(request, 'address.html', context)

		elif request.method =='GET' and UserInfo.address:
			context['form']=AddressForm()
			return render(request, 'address.html', context)

		form = AddressForm(request.POST, request.FILES)
		context['form']=form

		if not form.is_valid():
			context['error'] = _('Form values not valid')
			return render(request,'address.html', context)

		address = Address(door_no=form.cleaned_data['door_no'],
										street = form.cleaned_data['street'],
										village = form.cleaned_data['village'],
										town = form.cleaned_data['town'],
										city = form.cleaned_data['city'],
										state = form.cleaned_data['state'],
										pincode = form.cleaned_data['pincode']
										)
		address.save()
		UserInfo.address = address
		UserInfo.save()

		context['notify'] = _('address succesfully saved')
	except:
		context['error'] = _('failed to update address fetch save stores')	
	translation.activate(UserInfo.language)

	return render(request, 'address.html', context)

def confirm_registration(request, username, token):
	try:
		print username + "::" + token
		print User.objects.all()
		user = get_object_or_404(User, username=username)
    
		# Send 404 error if token is invalid
		if not default_token_generator.check_token(user, token):
			raise Http404

		# Otherwise token was valid, activate the user.
		user.is_active = True
		user.save()
	except:
		context ['User']=UserProfile.objects.get(user=request.user)

	return redirect(reverse('home'))

@login_required
def produceCategory(request):
	context ={}
	UserInfo = UserProfile.objects.get(user=request.user)
	context['User'] = UserInfo
	try:
		categories = ProduceCategory.objects.all()
		print categories
		context['categories'] = categories
	except:
		context['error']=_('Encountered while fetching categories')

	translation.activate(UserInfo.language)
	return render(request, 'produce_category.html', context)

@login_required
@transaction.atomic
def addProduceCategory(request):
	context ={}
	UserInfo = UserProfile.objects.get(user=request.user)
	context['User'] = UserInfo
	translation.activate(UserInfo.language)
	
	if not UserInfo.user_type=='2':
		context['error'] = _('Action not allowed for user type')
		return render(request, 'home.html', context)
	
	try:
		form = ProduceCategoryForm(request.POST,request.FILES)

		if not form.is_valid():
			return redirect(reverse('produce_category'))
		print "after"
		new_produce_category = ProduceCategory(name=form.cleaned_data['name'],pic=form.cleaned_data['pic'])
		print new_produce_category
		new_produce_category.save()
		context['notify'] =_('Produce category added successfully') 
	except:
		context['error']=_('Encountered while fetching categories')
	
	return redirect(reverse('produce_category'))

@login_required
def category_picture(request,categoryId):
	context ={}
	UserInfo = UserProfile.objects.get(user=request.user)
	context['User'] = UserInfo
	try:
		produce_category = get_object_or_404(ProduceCategory,id=categoryId)
		if not produce_category.pic:
			raise Http404
		content_type = guess_type(produce_category.pic.name)
	except: # catch *all* exceptions
		context['error']=_('Encountered while fetching image for the category')
		return redirect(reverse('produce_category'))

	return HttpResponse(produce_category.pic,content_type= content_type)

@login_required
def getProduce(request,categoryId):
	context ={}
	UserInfo = UserProfile.objects.get(user=request.user)
	context['User'] = UserInfo
	translation.activate(UserInfo.language)
	
	if not UserInfo.user_type=='2':
		context['error'] = _('Action not allowed for user type')
		return render(request, 'home.html', context)

	try:
		produceCategory = ProduceCategory.objects.filter(id=categoryId)
		if not produceCategory.exists():
			context['error'] = _('Prodcue Category not available')
			return render(request, 'home.html', context)
		produces = Produce.objects.filter(category=categoryId)
		context['produces'] = produces
		context['categoryId'] = categoryId

	except:
		context['error']=_('Encountered while fetching categories')

	
	return render(request, 'produce_in_category.html', context)

@transaction.atomic
@login_required
def addProduce(request):
	context ={}
	UserInfo = UserProfile.objects.get(user=request.user)
	context['User'] = UserInfo
	translation.activate(UserInfo.language)
	
	if not UserInfo.user_type=='2':
		context['error'] = _('Action not allowed for user type')
		return render(request, 'home.html', context)

	try:
		form = ProduceForm(request.POST,request.FILES)

		if not form.is_valid():
			return redirect(reverse('produce_category'))

		category = ProduceCategory.objects.get(id=str(request.POST['category']));
		new_produce = Produce(name=form.cleaned_data['name'],pic=form.cleaned_data['pic'],category=category)
		
		new_produce.save()
		context['notify'] = _('Produce added successfully')
        
	except:
		context ['error']=_('Encountered while fetching categories')

	translation.activate(UserInfo.language)
	return redirect('produce/'+str(request.POST['category']))

@login_required
def produce_picture(request,produceId):

	context ={}
	UserInfo = UserProfile.objects.get(user=request.user)
	context['User'] = UserInfo

	try:
		produce = get_object_or_404(Produce,id=produceId)
		if not produce.pic:
			raise Http404
		content_type = guess_type(produce.pic.name)
	except: # catch *all* exceptions
		context['error']=_('Encountered while fetching image for the category')
		return redirect(reverse('produce_in_category'))

	return HttpResponse(produce.pic,content_type= content_type)

@transaction.atomic
@login_required
def createDemand(request,produceId):
	context ={}
	UserInfo = UserProfile.objects.get(user=request.user)
	context['User'] = UserInfo
	translation.activate(UserInfo.language)
	
	if not UserInfo.user_type=='2':
		context['error'] = _('Action not allowed for user type')
		return render(request, 'home.html', context)

	try:
		translation.activate(UserInfo.language)

		if not Produce.objects.filter(id=produceId).exists():
			context['error'] = 'Produce not available'
			return render(request, 'home.html', context)

		produce = Produce.objects.get(id=produceId)
		context['produce'] = produce

		if request.method == 'GET':
			form = DemandsForm()#(exclude={'username'})
			context['form'] = form
			
			print produce
			return render(request, 'create_demand.html', context)

		form = DemandsForm(request.POST)
		context['form']=form
		
		if not form.is_valid():
			context['error'] = _('form is not valid')
			return render(request, 'create_demand.html', context)

		new_demand = Demands(quantity=form.cleaned_data['quantity'],price=form.cleaned_data['price'],produce=produce,buyer=request.user,delivery_datetime = form.cleaned_data['deldatetime'],bid_end_datetime=form.cleaned_data['biddatetime'])
		new_demand.save()
		context['notify'] = _('demand created')
		demands = Demands.objects.filter(buyer=request.user).order_by('delivery_datetime').reverse()
		context['demands'] = demands

	except: # catch *all* exceptions
		context['error']=_(' Encountered while creating a demand for the produce')
		translation.activate(UserInfo.language)
		return render(request, 'create_demand.html', context)

	translation.activate(UserInfo.language)
	return render(request, 'demands.html', context)

@login_required
def viewDemands(request):
	context ={}
	UserInfo = UserProfile.objects.get(user=request.user)
	context['User'] = UserInfo
	translation.activate(UserInfo.language)
	
	if not UserInfo.user_type=='2':
		context['error'] = _('Action not allowed for user type')
		return render(request, 'home.html', context)

	try:
		demands = Demands.objects.filter(buyer=request.user).order_by('delivery_datetime').reverse()
		context['demands'] = demands
	except:
		context['error'] = _('failed to fetch demands')

	translation.activate(UserInfo.language)
	return render(request, 'demands.html', context)

@login_required
def searchDemands(request):
	context = {}
	UserInfo = UserProfile.objects.get(user=request.user)
	context['User'] = UserInfo
	translation.activate(UserInfo.language)
	
	if not UserInfo.user_type=='1':
		context['error'] = _('Action not allowed for user type')
		return render(request, 'home.html', context)

	context['categories'] = ProduceCategory.objects.all().order_by('name')
	context['produces'] = Produce.objects.all().order_by('name')

	currentTime = timezone.make_aware(datetime.now(),timezone.get_default_timezone())

	try:
		demands = Demands.objects.filter(bid_end_datetime__gt=currentTime).exclude(id__in=(Bids.objects.filter(status=1).values_list('demand')))
		if request.method == 'GET':
			context['demands'] = demands
			return render(request, 'search_demands.html', context)
	
		print request.POST
		category = request.POST['category']
		produce = request.POST['produce']
		gt_quantity = (request.POST["gt_quantity"])
		lt_quantity = (request.POST["lt_quantity"])
		eq_quantity = (request.POST["eq_quantity"])
		gt_price = request.POST["gt_price"]
		lt_price = request.POST["lt_price"]
		eq_price = request.POST["eq_price"]

		if not category == "":
			if not ProduceCategory.objects.get(name=category):
				context['errors'] = _("Prodcue Category not available")
			else:
				demands = demands.filter(produce__in=Produce.objects.filter(category=ProduceCategory.objects.get(name=category)))
		if not produce =="":
			if not Produce.objects.get(name=produce):
				context['errors'] += _("Prodcue not available for given category")
			else:
				demands = demands.filter(produce__in=Produce.objects.filter(name=produce))
	
		if eq_quantity =="" and not gt_quantity =="":
			demands = demands.filter(quantity__gt=int(gt_quantity))
		if eq_quantity =="" and not lt_quantity =="":
			demands = demands.filter(quantity__lt=int(lt_quantity))
		if not eq_quantity == "":
			demands = demands.filter(quantity=int(eq_quantity))

		if eq_price =="" and not gt_price =="":
			demands = demands.filter(price__gt=int(gt_price))
		if eq_price =="" and not lt_price =="":
			demands = demands.filter(price__lt=int(lt_price))
		if not eq_price == "":
			demands = demands.filter(price=int(eq_price))

		context['demands'] = demands
	except:
		context['error'] = _("failed to perform search")
	translation.activate(UserInfo.language)
	return render(request, 'demands_table.html', context)

@login_required
def deleteDemand(request,demandId):
	context ={}
	UserInfo = UserProfile.objects.get(user=request.user)
	context['User'] = UserInfo

	if not UserInfo.user_type=='2':
		context['error'] = _('Action not allowed for user type')
		return render(request, 'home.html', context)

	try:
		
		if not Demands.objects.filter(id=demandId).exists():
			context['error'] = _('Demand not available')
			return render(request, 'home.html', context)

		demand = Demands.objects.get(id=demandId)
		
		if demand.getBidCount() != 0:
			context['error'] = _('Bids present for existing bid')
		elif not demand.buyer == request.user:
			context['warn'] = _('Users can only delete the demand that they posted')
		else:
			demand.delete()
			context['notify'] = _('demand deleted successfully')
		demands = Demands.objects.filter(buyer=request.user)
		context['demands'] = demands
	except:
		context['error'] = _('error occured while deleting the demand')

	translation.activate(UserInfo.language)
	return render(request, 'demands.html', context)

@login_required
@transaction.atomic
def createBid(request,demandId):
	context ={}
	UserInfo = UserProfile.objects.get(user=request.user)
	context['User'] = UserInfo
	translation.activate(UserInfo.language)
	
	if not UserInfo.user_type=='1':
		context['error'] = _('Action not allowed for user type')
		return render(request, 'home.html', context)

	try:
		
		if not Demands.objects.filter(id=demandId).exists():
			context['error'] = _('Demand not available in database')
			return render(request, 'search_demands.html', context)

		demand = Demands.objects.get(id=demandId)
		context['demand'] = demand
		
		print demand 
		

		if request.method == 'GET':
			form = BidsForm()#(exclude={'username'})
			context['form'] = form
			
			print form.fields
			return render(request, 'create_bid.html', context)

		form = BidsForm(request.POST)
		context['form']=form
		translation.activate(UserInfo.language)
		if not form.is_valid():
			context['error'] = _('form fileds are not valid')
			return render(request, 'create_bid.html', context)

		if form.cleaned_data['pickup_datetime']>demand.delivery_datetime:
			context['error'] = _('Pickup datetime should be less than the delivery datetime')
			return render(request, 'create_bid.html', context)

		if form.cleaned_data['confirmation_datetime']<demand.bid_end_datetime:
			context['error'] = _('Order Confirmation datetime should be greater than the bidding end datetime')
			return render(request, 'create_bid.html', context)

		if form.cleaned_data['confirmation_datetime']>demand.delivery_datetime:
			context['error'] = _('Order Confirmation datetime should be lesser than the delivery datetime')
			return render(request, 'create_bid.html', context)

		new_bid = Bids(seller=request.user,demand=demand,status='0',pickup_datetime=form.cleaned_data['pickup_datetime'],confirmation_datetime=form.cleaned_data['confirmation_datetime'])
		new_bid.save()

		existingOrder = Orders.objects.filter(bid__in=Bids.objects.filter(demand = new_bid.demand))

		print existingOrder
		if existingOrder.exists():
			context['error'] = _('The Order has already been accepted. Rejecting the present bid made')
			new_bid.status = 9
			new_bid.save()
			bids = Bids.objects.filter(seller=request.user).order_by('datetime').reverse()
			context['bids'] = bids
			return render(request, 'bids.html', context)

		buyer = UserProfile.objects.get(user=demand.buyer)
		context = sendSMS(request,str(buyer.phone),"A Bid has been placed on the Demand "+ demand.produce.name +" of quantity " + str(demand.quantity)+" .To view the bids for the demand, click on the following link : "+"http://%s%s" % (request.get_host(),"/demand-bids/"+demandId),context)
		
		context['notify'] = _('Bid Placed on demand')
		bids = Bids.objects.filter(seller=request.user).order_by('datetime').reverse()
		context['bids'] = bids
		return render(request, 'bids.html', context)


	except: # catch *all* exceptions
		context['error']=_(' Encountered while creating a bid for the demand')
		translation.activate(UserInfo.language)
		return render(request, 'create_bid.html', context)
	translation.activate(UserInfo.language)
	return redirect(reverse('view_bids'))

@login_required
def viewBids(request):
	context ={}
	UserInfo = UserProfile.objects.get(user=request.user)
	context['User'] = UserInfo

	translation.activate(UserInfo.language)
	
	if not UserInfo.user_type=='2'and not UserInfo.user_type=='1':
		context['error'] = _('Action not allowed for user type')
		return render(request, 'home.html', context)

	try:
		bids = Bids.objects.filter(seller=request.user).order_by('datetime').reverse()
		context['bids'] = bids
	except: # catch *all* exceptions
		context['error']=_(' Encountered while fetching bids')

	translation.activate(UserInfo.language)
	return render(request, 'bids.html', context)

@login_required
def searchBids(request):
	context ={}
	UserInfo = UserProfile.objects.get(user=request.user)
	context['User'] = UserInfo

	try:
		if request.method == 'GET':
			bids = Bids.objects.all()
			context['demands'] = bids
			context['categories'] = ProduceCategory.objects.all()
			context['produces'] = Produce.objects.all()

	except: # catch *all* exceptions
		context['error']=_(' Encountered while fetching bids')
		
	translation.activate(UserInfo.language)
	return render(request, 'search_bids.html', context)

@login_required
def deleteBid(request,bidId):
	context ={}
	UserInfo = UserProfile.objects.get(user=request.user)
	context['User'] = UserInfo
	translation.activate(UserInfo.language)
	
	if not UserInfo.user_type=='1':
		context['error'] = _('Action not allowed for user type')
		return render(request, 'home.html', context)

	try:
		bid_ob = Bids.objects.filter(id=bidId)
		if not bid_ob.exists():
			context['error'] = _('Bid not available')
			return render(request, 'home.html', context)

		bid = Bids.objects.get(id=bidId)
		if bid.status == '1':
			context['error'] = _('Bids has already been accepted. Please go and delete the order if you wish to cancel the order')
			bids = Bids.objects.filter(seller=request.user).order_by('datetime').reverse()
			context['bids'] = bids
			return render(request, 'bids.html', context)
		elif not bid.seller == request.user:
			context['warn'] = _('Users can only delete the Bid that they posted')
		else:
			bid.delete()
			context['notify'] = _('Bid deleted successfully')
		
		bids = Bids.objects.filter(seller=request.user).order_by('datetime').reverse()
		context['bids'] = bids
	except: # catch *all* exceptions
		context['error']=_(' Encountered while deleting the bid')
	
	return render(request, 'bids.html', context)

@login_required
def viewBidsforDemand(request,demandId):
	context ={}
	UserInfo = UserProfile.objects.get(user=request.user)
	context['User'] = UserInfo
	
	try:
		demand_ob = Demands.objects.filter(id=demandId)
		if not demand_ob.exists():
			context['error'] = _('Demand not available')
			return render(request, 'home.html', context)

		bids = Bids.objects.filter(demand=Demands.objects.get(id=demandId))
		context['bids'] = bids
	except:
		context['error']=_(' Encountered while fetching bids for the demand')
	translation.activate(UserInfo.language)
	return render(request, 'bids.html', context)
	
@login_required
@transaction.atomic
def rejectBid(request,bidId):
	context ={}
	UserInfo = UserProfile.objects.get(user=request.user)
	context['User'] = UserInfo

	if not UserInfo.user_type == '2':
		context['error'] = _("Action not allowed for User Type")
		return render(request, 'home.html', context)

	
	try:
		bid_ob = Bids.objects.filter(id=bidId)
		if not bid_ob.exists():
			context['error'] = _('Bid not available')
			return render(request, 'home.html', context)

		if not (bid.demand.buyer == request.user):
			context['warn'] = _('Users can only reject the bid that they have placed a demand for')
		else:
			bid = Bids.objects.get(id=bidId)
			bid.status = 9
			bid.save()
		
			seller = UserProfile.objects.get(user=bid.seller)
			context = sendSMS(request,str(seller.phone),_("Your Bid for the demand ")+ bid.demand.produce.name +_(" of quantity ") + str(bid.demand.quantity)+_(" has been rejected "),context)
		#.To place another bid on the demand, click on the following link : http://%s%s" % (request.get_host(),"/create-bid/"+bid.demand.id)

		bids = Bids.objects.filter(demand=bid.demand).order_by('pickup_datetime')
		context['bids'] = bids
		context['notify'] = _('Bid has been rejected')
	except:
		context['error'] = _('Occured while rejecting the bid')

	translation.activate(UserInfo.language)
	return render(request, 'bids.html', context)

@login_required
@transaction.atomic
def acceptOrder(request,bidId):
	context ={}
	UserInfo = UserProfile.objects.get(user=request.user)
	context['User'] = UserInfo
	translation.activate(UserInfo.language)
	
	if not UserInfo.user_type=='2':
		context['error'] = _('Action not allowed for user type')
		return render(request, 'home.html', context)

	
	try:
		bid_ob = Bids.objects.filter(id=bidId)
		if not bid_ob.exists():
			context['error'] = _('Bid not available')
			return render(request, 'home.html', context)

		bid = Bids.objects.get(id=bidId)
		if not (bid.demand.buyer == request.user):
			context['warn'] = _('Users can only accept the Order that they have placed a demand for')

		else:
			bid.status = 1
			bid.save()
			print bid
			context['notify'] = _('Bid has been accepted')
			bid.rejectOtherBids()
			context['info'] = _('All other bids have been rejected')
			order = Orders(bid=bid,status=0)
			order.save()
			seller = UserProfile.objects.get(user=bid.seller)
			context = sendSMS(request,str(seller.phone),_("Your Bid for the demand ")+ bid.demand.produce.name +_(" of quantity " )+ str(bid.demand.quantity)+_(" has been accepted. To view the order click on the link : ")+"http://%s%s" % (request.get_host(),"/orders/"),context)
			context['notify'] = _('Order has been placed')

	except:
		context['error'] = _('Occured while accepting the order')
	translation.activate(UserInfo.language)
	return redirect(reverse('view_orders'))

@login_required
@transaction.atomic
def deleteOrder(request,orderId):
	context ={}
	UserInfo = UserProfile.objects.get(user=request.user)
	context['User'] = UserInfo
	
	translation.activate(UserInfo.language)
	
	if not UserInfo.user_type=='2'and not UserInfo.user_type=='1':
		context['error'] = _('Action not allowed for user type')
		return render(request, 'home.html', context)

	
	try:
		order_ob = Orders.objects.filter(id=orderId)
		if not order_ob.exists():
			context['error'] = _('Order not available')
			return render(request, 'home.html', context)

		order = Orders.objects.get(id=orderId)
		if not (order.bid.demand.buyer == request.user or  order.bid.seller ==request.user):
			context['warn'] = _('Users can only delete the Order that they have')

		else:
			order.delete()
			seller = UserProfile.objects.get(user=order.bid.seller)
			print order.bid.demand
			context = sendSMS(request,str(seller.phone),"Order for "+ order.bid.demand.produce.name +" with quantity "+str(order.bid.demand.quantity)+" has been deleted",context)
			buyer = UserProfile.objects.get(user=order.bid.demand.buyer)
			context = sendSMS(request,str(buyer.phone),"Order for "+ order.bid.demand.produce.name +" with quantity "+str(order.bid.demand.quantity)+" has been deleted",context)
		
			Bids.objects.filter(id=order.bid.id).update(status='8')

			context['notify'] = _('Order has been deleted. The accepted bid has been cancelled')

		if UserInfo.user_type == "2":
			orders = Orders.objects.filter(bid__in=Bids.objects.filter(demand__in=Demands.objects.filter(buyer=request.user)))
		if UserInfo.user_type == "1":
			orders = Orders.objects.filter(bid__in=Bids.objects.filter(seller=request.user))
		context['orders'] = orders

	except:
		context['error'] = _('Occured while deleting the order')

	translation.activate(UserInfo.language)
	return render(request, 'orders.html', context)

@login_required
def viewOrders(request):
	context ={}
	UserInfo = UserProfile.objects.get(user=request.user)
	context['User'] = UserInfo
	
	try:
		if UserInfo.user_type == "2":
			orders = Orders.objects.filter(bid__in=Bids.objects.filter(demand__in=Demands.objects.filter(buyer=request.user)))
		if UserInfo.user_type == "1":
			orders = Orders.objects.filter(bid__in=Bids.objects.filter(seller=request.user))
		context['orders'] = orders
	except:
		context['error'] = _('Occured while fetching the orders')

	translation.activate(UserInfo.language)	
	return render(request, 'orders.html', context)

@login_required
def trackOrders(request):
	context ={}
	UserInfo = UserProfile.objects.get(user=request.user)
	context['User'] = UserInfo
	
	try:
		if UserInfo.user_type == "2":
			orders = Orders.objects.filter(bid__in=Bids.objects.filter(demand__in=Demands.objects.filter(buyer=request.user)))
		if UserInfo.user_type == "1":
			orders = Orders.objects.filter(bid__in=Bids.objects.filter(seller=request.user))
		context['orders'] = orders

	except:
		context['error'] = _('Occured while fetching the orders')

	translation.activate(UserInfo.language)	
	return render(request, 'track_orders.html', context)