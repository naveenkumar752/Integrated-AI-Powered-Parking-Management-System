from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(LicensePlate)
admin.site.register(ParkingSlot)
admin.site.register(ParkingTransaction)
admin.site.register(Transaction)

