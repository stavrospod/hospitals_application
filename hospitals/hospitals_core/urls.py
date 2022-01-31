from django.urls import path, register_converter
from datetime import datetime, timedelta

from . import views

app_name = 'hospitals_core'


urlpatterns = [
    # ex: /efhmereuonta.gr
    path('', views.index, name='index'),
    path('date/', views.date_filters, name='date-filters'),
    # ex: /efimereuonta-nosokomeia/athens
    path('efimereuonta-nosokomeia/<slug:region_slug>/', views.efimereuonta_ana_perioxi, name='efimereuonta-nosokomeia'),
]