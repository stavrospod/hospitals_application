from django.contrib import admin
from . models import *

# Register your models here.
admin.site.register(Region)
admin.site.register(Hospital)
admin.site.register(Clinic)
admin.site.register(Schedule)