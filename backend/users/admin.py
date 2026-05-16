from django.contrib import admin
from .models import UserProfile, Lawyer, Appointment
# Register your models here.

admin.site.register(UserProfile)
admin.site.register(Lawyer)
admin.site.register(Appointment)

