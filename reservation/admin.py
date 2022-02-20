from django.contrib import admin
from .models import Reservation, Blog

# Register your models here.
admin.site.register(Reservation)
admin.site.register(Blog)