import requests, re, pandas as pd
from sqlalchemy import create_engine
from dateparser.search import search_dates
from bs4 import BeautifulSoup
import camelot, pandas as pd
import numpy as np
from pandas import *
from scraping.models import *


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

def get_pdf_list(parsed_url):
    '''Gets list of pdfs of the last 5 days of pdfs from parsed html code'''
    soup = html_parser(parsed_url)
    #Get list of URLs including pdf files
    pdf_docs = soup.find_all('a', {'title': re.compile(r'.*\.pdf')})
    #Get list of titles and urls. NOTE: ENTER THE NUMBER OF DOCS
    try:
        pdf_json = []
        for pdf_doc in pdf_docs[:3]:
            pdf_title = pdf_doc.find(text=True, recursive = False).strip()
            pdf_url = parsed_url+pdf_doc.get('href').strip()
            onhold_date = search_dates(pdf_title, languages=['el'])[0][1]
            #Add to json item
            item = {"pdf_title": pdf_title, "pdf_url": pdf_url, "onhold_date":onhold_date}
            pdf_json.append(item)
    except:
        print(f"Error s101 {pdf_title}")
        raise Exception(f"Couldn't build json file with urls, title: {pdf_title} and onhold date")
    print("Page parsed and json has been built with doc title, url and onhold date")
    return pdf_json

'''TODO: Change to be secure'''
def pass_to_database(username, password, server, port, database, dataframe, table):
    engine = create_engine(f'postgresql://{username}:{password}@{server}:{port}/{database}', encoding='utf-8-sig')
    dataframe.to_sql(table, engine, if_exists='replace')

def runcsript():
    #Define the URL that you want to scrape:
    athens_hospitals_url = 'https://www.moh.gov.gr/articles/citizen/efhmeries-nosokomeiwn/68-efhmeries-nosokomeiwn-attikhs'


    pdf_json_info = get_pdf_list(athens_hospitals_url) #json data of hospitals
    '''Start of cleanup process
    for i, json_item in enumerate(pdf_json_info):
        if "ΟΡΘΗ ΕΠΑΝΑΚΟΙΝΟΠΟΙΗΣΗ" in json_item['pdf_title'] and json_item['onhold_date'] == pdf_json_info[i+1]['onhold_date']:
            pdf_json_info.pop(i+1)
    '''
    tables_received = []
    for pdf_item in pdf_json_info:
        pdf_url = pdf_item["pdf_url"]
        pdf_title = pdf_item["pdf_title"]
        onhold_date = pdf_item["onhold_date"]
        print(f"Getting thought the item with title: {pdf_title}")
        try:
            #Read pdf
            tables = camelot.read_pdf(pdf_url, pages ='1-end')
            number_of_tables = tables.n
            num_of_columns = len(tables[0].df.columns)
            print(f"num of tables: {number_of_tables}, num of columns: {num_of_columns}")
        except:
            print(f"Error s102 {pdf_title}")
            raise Exception(f"Couldn't parse the pdf file with title: {pdf_title}")
        '''Process to concat tables'''
        try:
            all_tables = []
            for i in range(number_of_tables):
                table = tables[i].df
                all_tables.append(table)
            concat_pdf_tables = pd.concat(all_tables, axis=0, ignore_index=True)
            concat_pdf_tables.rename(columns={concat_pdf_tables.columns[0]: "clinic" }, inplace = True) #Set first column to Clinic
            start_new_table_from = concat_pdf_tables.loc[concat_pdf_tables['clinic'].str.contains("ΚΛΙΝΙΚΕΣ|Κλινικές", case=False)].first_valid_index() #Returns the first id 
            concat_pdf_tables = concat_pdf_tables.iloc[start_new_table_from:].reset_index(drop=True)
            new_header = concat_pdf_tables.iloc[0] #grab the first row for the header
            concat_pdf_tables = concat_pdf_tables[1:] #take the data less the header row
            concat_pdf_tables.columns = new_header #set the header row as the df header
            concat_pdf_tables.reset_index(drop=True)
            concat_pdf_tables.rename(columns={concat_pdf_tables.columns[0]: "clinic" }, inplace = True) #Set first column to Clinic
            search = concat_pdf_tables.loc[concat_pdf_tables['clinic'].str.contains("ΚΛΙΝΙΚΕΣ|Κλινικές", case=False)] #Find and remove all the clinic rows
            final_results = concat_pdf_tables.drop(search.index.values).reset_index(drop=True)
            df_unpivoted = final_results.melt(id_vars=['clinic', 'ΠΑΡΑΤΗΡΗΣΕΙΣ'], var_name='onhold_time', value_name='hospital_names')
            df_unpivoted['hospital_names'].replace('', np.nan, inplace=True)
            df_unpivoted.dropna(subset=['hospital_names'], inplace=True)
            df_unpivoted = df_unpivoted.reset_index(drop=True)
            cleanup_process = df_unpivoted.rename(columns={"Clinic":"clinic", "ΠΑΡΑΤΗΡΗΣΕΙΣ":"note", "onhold_time":"onhold_hour", "hospital_names":"hospital_name"})
            cleanup_process.head()
            #cleanup_process = cleanup_process.replace({r'\s+$': '', r'^\s+': ''}, regex=True).replace(r'ΠΕΙΡΑΙΑΣ\n',  'ΠΕΙΡΑΙΑΣ ', regex=True) #remove this if needed
            cleanup_process = cleanup_process.replace({r'\s+$': '', r'^\s+': ''}, regex=True).replace(r'\nΠΕΙΡΑΙΑΣ \n',  ', ΠΕΙΡΑΙΑΣ ', regex=True)
            cleanup_process = cleanup_process.replace({r'\s+$': '', r'^\s+': ''}, regex=True).replace(r'\nΠΕΙΡΑΙΑΣ\n',  ' ΠΕΙΡΑΙΑΣ ', regex=True)
            cleanup_process = cleanup_process.replace({r'\s+$': '', r'^\s+': ''}, regex=True).replace(r'ΠΕΙΡΑΙΑΣ \n',  'ΠΕΙΡΑΙΑΣ ', regex=True)
            cleanup_process = cleanup_process.replace({r'\s+$': '', r'^\s+': ''}, regex=True).replace(r'Γ. \nΓΕΝΝΗΜΑΤΑΣ',  'Γ. ΓΕΝΝΗΜΑΤΑΣ', regex=True)
            cleanup_process = cleanup_process.replace({r'\s+$': '', r'^\s+': ''}, regex=True).replace(r'Η \nΠΑΜΜΑΚΑΡΙΣΤΟΣ',  'Η ΠΑΜΜΑΚΑΡΙΣΤΟΣ', regex=True)
            cleanup_process = cleanup_process.replace({r'\s+$': '', r'^\s+': ''}, regex=True).replace(r'ΑΓ. \nΠΑΝΤΕΛΕΗΜΩΝ',  'ΑΓ. ΠΑΝΤΕΛΕΗΜΩΝ', regex=True)
            cleanup_process = cleanup_process.replace({r'\s+$': '', r'^\s+': ''}, regex=True).replace(r'ΑΓΙΟΙ \nΑΝΑΡΓΥΡΟΙ',  'ΑΓΙΟΙ ΑΝΑΡΓΥΡΟΙ', regex=True)
            cleanup_process = cleanup_process.replace({r'\s+$': '', r'^\s+': ''}, regex=True).replace(r'ΑΓΙΟΣ \nΣΑΒΒΑΣ',  'ΑΓΙΟΣ ΣΑΒΒΑΣ', regex=True)
            cleanup_process = cleanup_process.replace({r'\s+$': '', r'^\s+': ''}, regex=True).replace(r'\nΝ.',  ', Ν.', regex=True)
            cleanup_process = cleanup_process.replace({r'\s+$': '', r'^\s+': ''}, regex=True).replace(r'\nΠ.',  ', Π.', regex=True)
            cleanup_process = cleanup_process.replace({r'\s+$': '', r'^\s+': ''}, regex=True).replace(r'\nΓ.',  ', Γ.', regex=True)
            cleanup_process = cleanup_process.replace({r'\s+$': '', r'^\s+': ''}, regex=True).replace(r'\nΨ.',  ', Ψ.', regex=True)
            cleanup_process = cleanup_process.replace({r'\s+$': '', r'^\s+': ''}, regex=True).replace(r'\n',  ' ', regex=True)
            separate_data = cleanup_process['hospital_name'].str.split(',').apply(Series, 1).stack()
            separate_data.index = separate_data.index.droplevel(-1)
            separate_data.name = 'hospital_name'
            del cleanup_process['hospital_name']
            final_data = cleanup_process.join(separate_data)
            final_data['onhold_date'] = onhold_date
            final_data['region'] = "Athens"
            final_data['hospital_name'] = final_data['hospital_name'].str.strip()
            final_data = final_data[final_data.hospital_name != 'ΠΕΙΡΑΙΑΣ']
            final_data = final_data.reset_index(drop=True)
            tables_received.append(final_data)
            print(f"Table for day: {onhold_date} and pdf {pdf_title} was added")
        except:
            print(f"Error s103 {table}")
            raise Exception(f"Couldn't build the table with na: {table}")


    df_merge = pd.concat(tables_received)
    df_merge.reset_index(drop=True)

    # Not able to iterate directly over the DataFrame
    df_records = df_merge.to_dict('region')
    return df_records

if __name__ == '__main__':
    # test1.py executed as script
    # do something
    runcsript()