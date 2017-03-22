from django.contrib import admin
#from easymode.i18n.admin.decorators import L10n
from farmConnect.models import Produce,ProduceCategory

admin.site.register(ProduceCategory)
admin.site.register(Produce)

# Register your models here.
