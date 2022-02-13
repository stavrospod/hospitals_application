from django.urls import path, register_converter
from datetime import datetime, timedelta

from . import views

app_name = 'hospitals_core'


urlpatterns = [
    # ex: /efhmereuonta.gr
    path('', views.index, name='index'),
    path('efimereuonta-nosokomeia/', views.index, name='index'),

    # ex: /efimereuonta-nosokomeia/athens
    path('efimereuonta-nosokomeia/<slug:region_slug>/', views.efimereuonta_ana_perioxi, name='efimereuonta-nosokomeia'),    

    # ex: efimereuonta-nosokomeia/athens/patholigiki
    path('efimereuonta-nosokomeia/<slug:region_slug>/<slug:clinic_slug>/', views.efimereuonta_nosokomeia, name='clinics-view'),

    # ex: efimereuonta-nosokomeia/athens/patholigiki/date
    path('efimereuonta-nosokomeia/<slug:region_slug>/<slug:clinic_slug>/results/<yyyy:date>/', views.efimereuonta_nosokomeia_results, name='date-clinics-view-results'),

    # ex: efimereuonta-nosokomeia/athens/patholigiki/date
    path('efimereuonta-nosokomeia/<slug:region_slug>/<slug:clinic_slug>/<yyyy:date>/', views.efimereuonta_nosokomeia_results, name='date-clinics-view-results'),
]