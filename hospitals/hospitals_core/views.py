from django.shortcuts import render
from django.http import HttpResponse, Http404
from .models import Schedule, Region, Hospital, Clinic
from datetime import datetime, timedelta
from django.core import serializers

today = datetime.now()
date_range = datetime.now()+timedelta(days=3)
date_filters = Schedule.objects.order_by('-onhold_date').distinct('onhold_date').filter(onhold_date__range = (today, date_range))

def date_filters(request):
    return render(request, 'hospitals_core/date_filter.html', {
        #Returns unique available regions in the DB
        'date_filters': date_filters
    })
    #{'date_filters': date_filters}

def index(request):
    '''This is the homepage that returns all. The available Regions in the DB.
    View: Index, HTML: Index.html URL: efhmereuonta.gr 
    '''
    return render(request, 'hospitals_core/index.html', {
        #Returns unique available regions in the DB
        'available_regions': Schedule.objects.all().distinct('region').exclude(region=None)
    })


def efimereuonta_ana_perioxi(request, region_slug):
    region= Region.objects.get(slug=region_slug)
    get_clinics = Schedule.objects.filter(region = region, onhold_date='2022-01-27').distinct('clinic').exclude(clinic=None)
    return render(request, 'hospitals_core/test.html', {
        'today': today,
        'region': region,
        'clinics': get_clinics,
        'date_filters': context[date_filters]
    })
