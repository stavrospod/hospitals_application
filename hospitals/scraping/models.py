import time
from django.db import models
from datetime import datetime, date
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save
from hospitals_core.models import *

def check_if_exists(model, model_value, created_value):
    lookup = '__'.join([model_value])
    if model.objects.filter(**{lookup: created_value}):
            print(f"{model_value} exists {created_value}")
    else:
        #Creates an object and assign it to region of the model on the other app
        model.objects.create(**{lookup: created_value})
        print(f"Updated {model_value}: {created_value}") 

# Create your models here.
class ScrapedHospitals(models.Model):
    clinic = models.CharField(max_length=250)
    note = models.CharField(max_length=250, blank=True, null=True)
    onhold_hour = models.CharField(max_length=50)
    hospital_name = models.CharField(max_length=250)
    onhold_date = models.DateField(default=date.today)
    region = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.hospital_name + "    "+ self.clinic
    class Meta:
        ordering = ['hospital_name']
    class Admin:
        pass


@receiver(post_save, sender=ScrapedHospitals)
def scraped_post_save(sender, instance, created, *args, **kwargs):
    if created:
        created_region = instance.region
        if created_region is not None:
            check_if_exists(Region, 'region', created_region)
        created_hospital = instance.hospital_name
        if created_hospital is not None:
            check_if_exists(Hospital, 'hospital_name', created_hospital)
        created_clinic = instance.clinic
        if created_clinic is not None:
            check_if_exists(Clinic, 'clinic', created_clinic)
        created_onhold_hour = instance.onhold_hour
        created_onhold_date = instance.onhold_date
        Schedule.objects.create(created_at = timezone.now())
        time.sleep(2)
        Schedule.objects.filter(id = Schedule.objects.latest('created_at').id).update(onhold_date = created_onhold_date, onhold_hour = created_onhold_hour, region = Region.objects.get(region = created_region), hospital = Hospital.objects.get(hospital_name = created_hospital), clinic = Clinic.objects.get(clinic = created_clinic))
        #Schedule.objects.filter(Schedule.objects.latest('created_at')).update(onhold_date = created_onhold_date)
        print(Schedule.objects.latest('created_at').id)