from django.contrib import admin
from .models import Registration, RegistAdmin
# Register your models here.
admin.site.register(Registration, RegistAdmin)
