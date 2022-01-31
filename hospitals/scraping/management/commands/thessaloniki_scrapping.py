# -*- coding: utf-8 -*- 
import requests, re, camelot, pandas as pd
import os
import numpy as np
import psycopg2
import sqlalchemy as db
from sqlalchemy import create_engine
from dateparser.search import search_dates
from bs4 import BeautifulSoup
from pandas import Series


def html_parser(url):
    '''Gets a URL to return the html parsed code to be used on a soup variable'''
    try:
        page = requests.get(url)
    except requests.exceptions.Timeout:
        #TODO: try again in 30 minutes (add trigger)
        pass
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    soup = BeautifulSoup(page.content, "html.parser")
    #returns HTML code of the website
    return soup

thessaloniki_hospitals_url = 'http://www.3ype.gr/index.php/menutop-enhmerosipoliton/menutop-efhmeries'

def runcsript():
    soup = html_parser(thessaloniki_hospitals_url)
    excel_files = soup.find_all('a', {'href':re.compile('.*(uploads).*')})

    excel_url='http://www.3ype.gr/' + excel_files[-1].get('href').strip()
    print("Reading excel file")
    tables = pd.read_excel(excel_url, skiprows=1)
    tables.rename(columns={tables.columns[0]: "hospital_name" }, inplace = True)
    tables.rename(columns={tables.columns[1]: "clinic" }, inplace = True)
    tables[['hospital_name', 'clinic']] = tables[['hospital_name','clinic']].fillna(method='ffill')
    tables.at[0, 'hospital_name'] = "hospital_name"
    tables.at[0, 'clinic'] = "clinic"
    new_header = tables.iloc[0] #grab the first row for the header
    tables = tables[1:] #take the data less the header row
    tables.columns = new_header #set the header row as the df header
    tables.reset_index(drop=True)
    print("Transforming")

    unpivoted_table = tables.copy()
    unpivoted_table = unpivoted_table.melt(id_vars=["hospital_name", "clinic"], var_name="onhold_date", value_name='onhold_clinic')
    unpivoted_table = unpivoted_table.reset_index(drop=True)

    final_data = unpivoted_table.copy()
    final_data.dropna(subset=['onhold_clinic'], inplace=True)
    final_data['region'] = "Thessaloniki"
    final_data['onhold_hour'] = ""
    final_data['notes'] = ""
    final_data = final_data[["clinic", "notes", "onhold_date", "hospital_name", "region", "onhold_hour"]]

    df_merge = final_data.replace({'clinic' : {'Παθ': 'Παθολογική', 'Καρδ': 'Καρδιολογική', 'Αιμοδ': 'Αιματολογική', 'Νευρολ': 'Νευρολογική', 'Χειρ': 'Χειρουργική', 'Ορθοπ': 'Ορθοπαιδική', 'Πλαστ.χειρ.': 'Πλαστ. Χειρουργική', 'ΩΡΛ': 'Ω.Ρ.Λ.', 'Γναθοχ': 'Γναθοχειρουργική', 'Νευροχ': 'Νευροχειρουργική', 'Θωρ/κή': 'Θωρακοχειρουργική', 'Καρδοχ': 'Καρδιοχειρ/κή', 'Οφθ': 'Οφθαλμολογική', 'Αγγειοχ': 'Αγγειοχειρ/κή', 'Πνευμον.': 'Πνευμονολογική', 'Παιδοψυχ.': 'Παιδοψυχιατρική', 'Ψυχ': 'Ψυχιατρική', 'Ουρ': 'Ουρολογική', 'Οδον': 'Οδοντιατρική', 'Γυν': 'Γυναικολογική', 'Παιδ': 'Παιδιατρικό', 'Νεογν': 'Νεογνολογική', 'Μ/Γ': 'Μονάδα Γενετικής', 'Παιδοχ': 'Παιδοχειρουργική', 'Παιδοορθ': 'Παιδοοδοντιατρική'}})
    df_merge = df_merge.reset_index(drop=True)
    # Not able to iterate directly over the DataFrame
    df_records = df_merge.to_dict('region')
    return df_records
    '''
    notes = unpivoted_table[unpivoted_table['clinic'].str.len()>15]
    notes = notes['clinic'].drop_duplicates()
    notes = notes.to_frame('notes')
    notes = notes.reset_index(drop=True)
    '''

if __name__ == '__main__':
    # test1.py executed as script
    # do something
    runcsript()