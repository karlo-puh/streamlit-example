from collections import namedtuple
from typing import Iterable
import altair as alt
import math
import os
import pandas as pd
#from scrapy.http import Request
import streamlit as st
from bs4 import BeautifulSoup
import requests
import json
import time
from woocommerce import API
import psutil
from bs4 import BeautifulSoup
import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--disable-features=NetworkService")
options.add_argument("--window-size=1920x1080")
options.add_argument("--disable-features=VizDisplayCompositor")


def delete_selenium_log():
    if os.path.exists('selenium.log'):
        os.remove('selenium.log')


def show_selenium_log():
    if os.path.exists('selenium.log'):
        with open('selenium.log') as f:
            content = f.read()
            st.code(content)


def run_selenium():
    name = str()
    with webdriver.Chrome(options=options, service_log_path='selenium.log') as driver:
        url = "https://www.unibet.fr/sport/football/europa-league/europa-league-matchs"
        driver.get(url)
        xpath = '//*[@class="ui-mainview-block eventpath-wrapper"]'
        # Wait for the element to be rendered:
        element = WebDriverWait(driver, 10).until(lambda x: x.find_elements(by=By.XPATH, value=xpath))
        name = element[0].get_property('attributes')[0]['name']
    return name

if 'Img Url' not in st.session_state:
    st.session_state['Img Url'] = 'invalid'
 
if 'Dimensions' not in st.session_state:                   
    st.session_state['Dimensions'] = "20x30"


months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
st.set_page_config(layout="wide")

wcapi = API(
    url="https://www.strucnaliteratura.hr",
    consumer_key="ck_f2b5bb4942ed9dd74e6a39010ea9e89f94b787e5",
    consumer_secret="cs_d70cd5e633e36012e910dc8a97eb1435325e676f",
    version="wc/v3",
    wp_api=True,
    timeout=10000
)

def routledge_scrape(url):
    try:
        result = run_selenium()
        st.info(f'Result -> {result}')
        st.info('Successful finished. Selenium log file is shown below...')
        show_selenium_log()
        #soup = BeautifulSoup(driver.page_source, 'html.parser')
        #print(soup)
        #print("not working")

        '''
        meta_tags = soup.find_all('meta', attrs={'property': True})

        for meta in meta_tags:
            if meta['property'] == 'product:price:amount':
                print(meta['content'])

        price = meta_tags.find()
        
        # Extracting Title and Subtitle
        title_with_subtitle = soup.find('h1', class_='visible-xs').text.strip()
        title_parts = title_with_subtitle.split(':')
        title = title_parts[0].strip()
        subtitle = title_parts[1].strip() if len(title_parts) > 1 else None

        # Extracting Authors
        authors = ', '.join(a.text.strip() for a in soup.find_all('a', class_='product-authors'))

        # Extracting Year, Pages, and ISBN
        year = None
        pages = None
        isbn = None
        for span in soup.find_all('span'):
            text = span.text.strip()
            if text.startswith('ISBN:'):
                isbn = text.split(': ')[1].replace('-','')
            elif any(month in text for month in months):
                year = text.split()[-1]
            elif text.endswith('Pages'):
                pages = text.split()[0]
        
        # Extracting Description, Format, Image URL, Price (Euro), and Category
        description = soup.find('section', class_='product-long-description').find('div', class_='description').text.strip()

        format_section = soup.find('div', class_='type-of-book')
        format = format_section.find('b').text.strip()

        image_url = soup.find('div', class_='item-image').find('img')['data-src']

        price = soup.find('div', class_='product-price-wr').find('p', class_='pr-price').text.strip()

        category_list = soup.find('ul', class_='breadcrumbs')
        category = '/'.join([li.text.strip() for li in category_list.find_all('li')])
        
        return {
            'Title': title,
            'Subtitle': subtitle,
            'Authors': authors,
            'Year': year,
            'Pages': pages,
            'Description': description,
            'Format': format,
            'Image URL': 'image_url',
            'Price (Euro)': price,
            'ISBN': isbn,
            'Category': category
        }
        '''
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return {'Error' : 'Invalid URL'}

    
def wiley_scrape(url):
    try:
        page = requests.get(url)
        page.raise_for_status()
        soup = BeautifulSoup(page.content, 'html.parser')
        
        # Extracting Title and Subtitle
        title_with_subtitle = soup.find('h1', class_='visible-xs').text.strip()
        title_parts = title_with_subtitle.split(':')
        title = title_parts[0].strip()
        subtitle = title_parts[1].strip() if len(title_parts) > 1 else None

        # Extracting Authors
        authors = ', '.join(a.text.strip() for a in soup.find_all('a', class_='product-authors'))

        # Extracting Year, Pages, and ISBN
        year = None
        pages = None
        isbn = None
        for span in soup.find_all('span'):
            text = span.text.strip()
            if text.startswith('ISBN:'):
                isbn = text.split(': ')[1].replace('-','')
            elif any(month in text for month in months):
                year = text.split()[-1]
            elif text.endswith('Pages'):
                pages = text.split()[0]
        
        # Extracting Description, Format, Image URL, Price (Euro), and Category
        description = soup.find('section', class_='product-long-description').find('div', class_='description').text.strip()

        format_section = soup.find('div', class_='type-of-book')
        format = format_section.find('b').text.strip()

        image_url = soup.find('div', class_='item-image').find('img')['data-src']

        price = soup.find('div', class_='product-price-wr').find('p', class_='pr-price').text.strip()

        category_list = soup.find('ul', class_='breadcrumbs')
        category = '/'.join([li.text.strip() for li in category_list.find_all('li')])

        return {
            'Title': title,
            'Subtitle': subtitle,
            'Authors': authors,
            'Year': year,
            'Pages': pages,
            'Description': description,
            'Format': format,
            'Image URL': image_url,
            'Price (Euro)': price,
            'ISBN': isbn,
            'Category': category
        }
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return {'Error' : 'Invalid URL'}



start_memory_usage = psutil.virtual_memory().used

print(f"Memory usage increased by {start_memory_usage / (1024 * 1024):.2f} MB")


"""

# Book Import
"""


@st.cache_data
def get_categories():
    avalible_categories = {}
    for page in range(1,3):
        json_categories = json.loads(wcapi.get("products/categories", params={'per_page' : 100, 'page' : page}).text)

        for category in json_categories:

            full_path = "";

            i = 0
            parent_id = category["parent"]

            while parent_id != "" and i < len(json_categories):
                if json_categories[i]["id"] == parent_id:
                    parent_id = json_categories[i]["parent"]
                    full_path = json_categories[i]["name"] + "/"
                    i = 0
                else:
                    i+= 1
                
            full_path += category["name"]
            avalible_categories[full_path] = category["id"]
        return avalible_categories

avalible_categories = get_categories()

link = st.text_input(label = 'Input URL Here', label_visibility = 'collapsed')

submitted = st.button("Search")

clear = st.button("Clear Form")

if submitted:
    if(link.__contains__('routledge')):
        book_data = routledge_scrape(link)
    else:
        book_data = wiley_scrape(link)
    
    while book_data is None:
            st.spinner('Wait for it...')
    if(book_data.get('Error')):
        st.warning(book_data.get('Error'))
        st.stop()
    else:
        st.success('Done!')

    #st.text(link)
    st.session_state["ISBN"] = book_data.get('ISBN','');
    st.session_state["Title"] = book_data.get('Title','');
    st.session_state["Subtitle"] = book_data.get('Subtitle',''); 
    st.session_state["Authors"] = book_data.get('Authors',''); 
    st.session_state["Year"] = book_data.get('Year',''); 
    st.session_state["Pages"] = book_data.get('Pages',''); 
    st.session_state["Format"] = book_data.get('Format',''); 
    st.session_state["Price (Euro)"] = book_data.get('Price (Euro)',''); 
    st.session_state["Category"] = book_data.get('Category',''); 
    st.session_state["Description"] = book_data.get('Description',''); 
    st.session_state['Img Url'] = book_data.get('Image URL', '')

if clear:
    st.session_state["ISBN"] = '';
    st.session_state["Title"] = '';
    st.session_state["Subtitle"] = ''; 
    st.session_state["Authors"] = ''; 
    st.session_state["Year"] = ''; 
    st.session_state["Pages"] = ''; 
    st.session_state["Format"] = ''; 
    st.session_state["Price (Euro)"] = ''; 
    st.session_state["Category"] = ''; 
    st.session_state["Description"] = '';
    st.session_state["selected_category"] = None; 

with st.form("show_book_form"):

    col1, col2 = st.columns([4, 2])
    
    with col1: 
        subcol1, subcol2 = st.columns(2)

        with subcol1:
            isbn = st.text_input('ISBN', key = 'ISBN')
            title = st.text_input('Title', key = 'Title')
            subtitle = st.text_input('Subtitle', key = 'Subtitle')
            authors = st.text_input('Authors', key = 'Authors')

        with subcol2:
            year = st.text_input('Year', key = 'Year')
            pages = st.text_input('Pages', key = 'Pages')
            format = st.text_input('Format', key = 'Format')
            price = st.text_input('Price (Euro)', key = 'Price (Euro)')

        category = st.text_input('Category', key = 'Category')
        description = st.text_area('Description', height= 400, key = 'Description')   

    if st.session_state['Img Url'] != 'invalid':
        with col2: 
            st.image(
                st.session_state['Img Url'],
                use_column_width=True
        )

    submited = st.form_submit_button("Submit")


option = st.selectbox(
    "Odaberite kategoriju",
    avalible_categories.keys(),
    index=None,
    placeholder="Kategorija...",
    key = 'selected_category'
    )

if st.button("Import"):
    
    for item in st.session_state:
        print(str(item) + ":" + str(st.session_state[item]))

    json_category_list = [{}]
    category_string = st.session_state['selected_category']

    json_category_list.append({"id" : avalible_categories[category_string]})
    while category_string.find('/') > 0:
        print(category_string)
        category_string = category_string.rsplit('/',1)[0]
        json_category_list.append({"id" : avalible_categories[category_string]})


    #wcapi.post("products/attributes/7/terms", data = {"name" = st.session_state['Authors'].rsplit(', ')})

    print(wcapi.post("products/attributes/8/terms", {"name" :  str(st.session_state['Year']) + "."}).json())
    print(wcapi.post("products/attributes/5/terms", {"name" :  "Wiley"}).json())
    print(wcapi.post("products/attributes/6/terms", {"name" :  "English"}).json())
    print(wcapi.post("products/attributes/1/terms", {"name" :  st.session_state['Format']}).json())
    print(wcapi.post("products/attributes/12/terms", {"name" : st.session_state['ISBN']}).json())
    print(wcapi.post("products/attributes/7/terms", {"name" : st.session_state['Dimensions']}).json())

    data = {
        "name": st.session_state['Title'],
        "type": "simple",
        "status":"publish",
        "featured": "false",
        "catalog_visibility":"visible",
        "description": st.session_state['Description'],
        "short_description": "",
        "sku": st.session_state['ISBN'],
        "price": st.session_state['Price (Euro)'],
        "regular_price": st.session_state['Price (Euro)'],

        "lang":"en",
        
        #"sale_price":"",
        #"on_sale" : False,

                
        "tax_status":"taxable",
        "tax_class":"5-pdv-a",
        "manage_stock": "false",
        "backorders":"no",
        "backorders_allowed": "false",
        "backordered": "true",

        
        #"weight":"",
        #"dimensions":{
        #    "length":"",
        #    "width":"",
        #    "height":""
        #},

        "categories": json_category_list,

        "images": [
            {
                "src": st.session_state['Img Url'],
                "name": st.session_state['ISBN'],
                "alt": st.session_state['ISBN'] + "Book Cover Picture"
            }
        ],

        "attributes":[
            {
                "id":7,
                "name":"autor",
                "position":1,
                "visible":"true",
                "variation":"false",
                "options":st.session_state['Authors'].rsplit(', ')
            },
            {
                "id":8,
                "name":"god. izdanja",
                "visible":"true",
                "variation":"false",
                "options":[
                    str(st.session_state['Year']) + "."
                ]
            },
            {
                "id":5,
                "name":"izdavač",
                "position":3,
                "visible":"true",
                "variation":"false",
                "options":[
                    str("Wiley")
                ]
            },
            {
                "id":6,
                "name":"jezik",
                "position":4,
                "visible":"true",
                "variation":"false",
                "options":[
                    str("English")
                ]
            },
            {
                "id":1,
                "name":"uvez",
                "position":5,
                "visible":"true",
                "variation":"false",
                "options":[
                    str(st.session_state['Format'])
                ]
            },
            {
                "id":12,
                "name":"ISBN",
                "position":6,
                "visible":"true",
                "variation":"false",
                "options":[
                    str(st.session_state['ISBN'])
                ]
            },
            {
                "id":20,
                "name":"dimenzije",
                "position":7,
                "visible":"true",
                "variation":"false",
                "option":[
                    str(st.session_state['Dimensions'])
                ]
            }
        ],

    }
    print("\n\n")
    print(data)
    #print(wcapi.get("products", params={id : 35433}).json())  
    #print(wcapi.post("products", data).json())
    #print(data)

    st.text("Book named " + str( st.session_state['Title'] ) + " was imported to category " + str(st.session_state['selected_category']))



