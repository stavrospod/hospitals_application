import requests, re, pandas as pd
from sqlalchemy import create_engine
from dateparser.search import search_dates
from bs4 import BeautifulSoup
import camelot, pandas as pd
import numpy as np
from pandas import *
from scraping.models import *
from scraping.management.commands import athens_scrapping, thessaloniki_scrapping


athens_records = athens_scrapping.runcsript()
thessaloniki_records = thessaloniki_scrapping.runcsript()

def add_to_the_db(df_records):
    '''
    Function that adds to the DB all the records from the hospitals
    '''
    info_missing = []
    for record in df_records:
        if record['clinic'] == '' or record['hospital_name']== '' or record['onhold_date']=='' or record['region']=='':
            info_missing.append(record)
            print(f"{info_missing}")
            continue
        ScrapedHospitals.objects.create(clinic = record['clinic'], 
        onhold_hour=record['onhold_hour'], 
        hospital_name=record['hospital_name'],
        onhold_date=record['onhold_date'],
        region=record['region']
        )
    print(f"Items missed {info_missing}")

print(f"Adding data for ATHENS")
add_to_the_db(athens_records)
print(f"Adding data for THESSALONIKI")
add_to_the_db(thessaloniki_records)