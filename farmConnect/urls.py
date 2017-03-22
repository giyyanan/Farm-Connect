"""webapps URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views

from django.contrib.auth import views as auth_views
from farmConnect import views

urlpatterns = [
	url(r'^$', views.home,name='home'),
	url(r'^login', auth_views.login, {'template_name':'login.html'}, name='login'),
    url(r'^admin/', include(admin.site.urls)),
   #Route to logout a user and send them back to the login page 
	url(r'^logout', auth_views.logout_then_login, name='logout'),
	url(r'^register', views.register , name='register'),
    url(r'^account', views.account , name='account'),
    url(r'^profile', views.profile , name='profile'),
    url(r'^address', views.address , name='address'),
    #url(r'^stores', views.stores , name='stores'),

	url(r'^categories', views.produceCategory , name='produce_category'),
	#url(r'^add-category', views.addProduceCategory , name='add_produce_category'),
	url(r'^category_picture/(?P<categoryId>\w+)$', views.category_picture,name='category_pic'),

	url(r'^produce/(?P<categoryId>\w+)$', views.getProduce , name='produce_in_category'),
	url(r'^add-produce', views.addProduce, name='add_produce'),
	url(r'^produce_picture/(?P<produceId>\w+)$', views.produce_picture,name='produce_pic'),

    url(r'^create-demand/(?P<produceId>\w+)$', views.createDemand , name='create_demand'),
    url(r'^delete-demand/(?P<demandId>\w+)$', views.deleteDemand , name='delete_demand'),
    url(r'^demands', views.viewDemands , name='view_demands'),
    url(r'^search-demands',views.searchDemands, name='search_demands'),
    url(r'^demand-bids/(?P<demandId>\w+)$',views.viewBidsforDemand, name='view_demand_bids'),

    url(r'^create-bid/(?P<demandId>\w+)$', views.createBid, name='create_bid'),
    url(r'^delete-bid/(?P<bidId>\w+)$', views.deleteBid , name='delete_bid'),
	url(r'^bids', views.viewBids , name='view_bids'),

    #url(r'^search-bids',views.searchBids, name='search_Bids'),

    url(r'^accept-order/(?P<bidId>\w+)$', views.acceptOrder , name='accept_order'),
    url(r'^reject-bid/(?P<bidId>\w+)$', views.rejectBid , name='reject_bid'),
    url(r'^delete-order/(?P<orderId>\w+)$', views.deleteOrder , name='delete_order'),

    url(r'^orders', views.viewOrders , name='view_orders'),
    url(r'^track-orders', views.trackOrders , name='track_orders'),

    url(r'^confirm-registration/(?P<username>[a-zA-Z0-9_@\+\-]+)/(?P<token>[a-z0-9\-]+)$',views.confirm_registration, name='confirm'),
]