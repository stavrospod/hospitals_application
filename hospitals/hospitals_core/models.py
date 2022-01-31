import unidecode
from unidecode import unidecode
from django.db import models
from django.utils import timezone
from datetime import datetime, date
from django.utils.text import slugify
from django.urls import reverse


# Create your models here.
class Region(models.Model):
    region = models.CharField(max_length=100, unique=True)
    region_display = models.CharField(max_length=100, unique=True, null=True)
    slug = models.SlugField(max_length=255, unique=False, null=True)

    def __str__(self):
        return self.region

    def save(self, *args, **kwargs):
            if not self.slug:
                self.slug = slugify(unidecode(self.region))
            super(Region, self).save(*args, **kwargs)

class Hospital(models.Model):
    hospital_name = models.CharField(max_length=100, unique=True, blank=True, null=True)
    actual_name = models.CharField(max_length=100, unique=True, blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=False, null=True)

    def __str__(self):
        return self.hospital_name

    def save(self, *args, **kwargs):
            if not self.slug:
                self.slug = slugify(unidecode(self.hospital_name))
            super(Hospital, self).save(*args, **kwargs)

class Clinic(models.Model):
    clinic = models.CharField(max_length=100, unique=True, blank=True, null=True)
    clinic_display = models.CharField(max_length=100, unique=True, blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=False, null=True)

    def __str__(self):
        return self.clinic

    def save(self, *args, **kwargs):
            if not self.slug:
                self.slug = slugify(unidecode(self.clinic))
            super(Clinic, self).save(*args, **kwargs)

class Schedule(models.Model):
    onhold_hour = models.CharField(max_length=50, blank=True, null=True)
    onhold_date = models.DateField(default=date.today)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, null=True, related_name="area")
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, null=True, related_name="available_hospital")
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, null=True, related_name="clinic_type")
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Date: {self.onhold_date} - Hour: {self.onhold_hour} - Region: {self.region} - Hospital: {self.hospital} - Clinic: {self.clinic} " 
