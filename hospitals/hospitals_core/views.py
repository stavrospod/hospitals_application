from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, Http404
from django.urls import register_converter
from .models import Schedule, Region, Hospital, Clinic
from datetime import datetime, timedelta
from django.core import serializers

today = datetime.now()
date_range = datetime.now()+timedelta(days=3)

class DateConverter:
    regex = '\d{4}-\d{2}-\d{2}'

    def to_python(self, value):
        return datetime.strptime(value, '%Y-%m-%d')

    def to_url(self, value):
        return value
register_converter(DateConverter, 'yyyy')



def index(request):
    '''This is the homepage that returns all. The available Regions in the DB.
    View: Index, HTML: Index.html URL: efhmereuonta.gr 
    '''
    return render(request, 'hospitals_core/index.html', {
        #Returns unique available regions in the DB
        'available_regions': Schedule.objects.all().distinct('region').exclude(region=None)
    })


def efimereuonta_ana_perioxi(request, region_slug):
    '''This is the page that will include all the
    available clinics in one Region.
    URL ex: /efimereuonta-nosokomeia/athens
    '''
    region = Region.objects.get(slug=region_slug)
    return render(request, 'hospitals_core/efimereuonta_per_region.html', {
        'available_clinics': region.area.all().distinct('clinic').exclude(clinic=None),
        'region': region,
        'region_slug': region_slug
    })


def efimereuonta_nosokomeia(request, region_slug, clinic_slug, **date_filters):
    clinic = Clinic.objects.get(slug=clinic_slug)
    region = Region.objects.get(slug=region_slug)
    get_clinics_id = Clinic.objects.get(slug = clinic_slug).id
    get_region_id = Region.objects.get(slug = region_slug).id
    default_date = today
    recent_dates = Schedule.objects.order_by('onhold_date').distinct('onhold_date').filter(onhold_date__range = (today, date_range), region = get_region_id)
    date_filters = recent_dates
    return render(request, 'hospitals_core/efimereuonta_nosokeia.html', {
        'available_hospitals': Schedule.objects.filter(region = get_region_id, clinic=get_clinics_id, onhold_date=default_date),
        'region': region,
        'clinic': clinic,
        'date_filters': date_filters,
        'region_slug': region_slug,
        'clinic_slug': clinic_slug

    })

@csrf_exempt
def efimereuonta_nosokomeia_results(request, date, region_slug, clinic_slug, **date_filters):
    clinic = Clinic.objects.get(slug=clinic_slug)
    region = Region.objects.get(slug=region_slug)
    get_clinics_id = Clinic.objects.get(slug = clinic_slug).id
    get_region_id = Region.objects.get(slug = region_slug).id
    default_date = today
    recent_dates = Schedule.objects.order_by('onhold_date').distinct('onhold_date').filter(onhold_date__range = (today, date_range), region = get_region_id)
    date_filters = recent_dates
    if request.method == "POST":
        print(f'{date}')
        return render(request, 'hospitals_core/results.html', {
        'available_hospitals': Schedule.objects.filter(region = get_region_id, clinic=get_clinics_id, onhold_date=date),
        'region': region,
        'clinic': clinic,
        'date_filters': date_filters
    })
    else:
        return render(request, 'hospitals_core/efimereuonta_nosokeia.html', {
        'available_hospitals': Schedule.objects.filter(region = get_region_id, clinic=get_clinics_id, onhold_date=default_date),
        'region': region,
        'clinic': clinic,
        'date_filters': date_filters
    })