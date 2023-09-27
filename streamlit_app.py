from collections import namedtuple
import altair as alt
import math
import os
import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup
import requests
import json
import time
from woocommerce import API

months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
st.set_page_config(layout="wide")

wcapi = API(
    url="https://www.strucnaliteratura.hr",
    consumer_key="ck_f2b5bb4942ed9dd74e6a39010ea9e89f94b787e5",
    consumer_secret="cs_d70cd5e633e36012e910dc8a97eb1435325e676f",
    version="wc/v3"
)


if 'Img Url' not in st.session_state:
    st.session_state['Img Url'] = ''
 
if 'Dimensions' not in st.session_state:                   
    st.session_state['Dimensions'] = "20x30"

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

"""

# Book Import
"""

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


link = st.text_input(label = '', label_visibility = 'collapsed')

submitted = st.button("Search")

clear = st.button("Clear Form")

if submitted:
    book_data = wiley_scrape(link)
    
    while book_data is None:
            st.spinner('Wait for it...')
    if(book_data.get('Error')):
        st.warning(book_data.get('Error'))
        st.stop()
    else:
        st.success('Done!')

    st.text(link)
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

    if st.session_state['Img Url'] != '':
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
    
    json_category_list = [{}]
    category_string = st.session_state['selected_category']

    json_category_list.append({"id" : avalible_categories[category_string]})
    while category.find('/') > 0:
        category_string = category_string.rsplit('/',1)[0]
        json_category_list.append({"id" : avalible_categories[category_string]})


    data = {
        "name": st.session_state['Title'],
        "type": "simple",
        "status":"publish",
        "featured": False,
        "catalog_visibility":"visible",
        "description": st.session_state['Description'],
        "short_description": "",
        "sku": st.session_state['ISBN'],
        "price": st.session_state['Price (Euro)'],
        "regular_price": st.session_state['Price (Euro)'],

        
        #"sale_price":"",
        #"on_sale" : False,

                
        "tax_status":"taxable",
        "tax_class":"5-pdv-a",
        "manage_stock": False,
        "backorders":"no",
        "backorders_allowed":False,
        "backordered": True,

        
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
                "visible": True,
                "variation": False,
                "options": st.session_state['Authors'].rsplit(', ')
            },
            {
                "id":8,
                "name":"god. izdanja",
                "position":2,
                "visible": True,
                "variation": False,
                "options":[
                    st.session_state['Year']
                ]
            },
            {
                "id":5,
                "name":"izdava\u010d",
                "position":3,
                "visible": True,
                "variation": False,
                "options":[
                    "Wiley"
                ]
            },
            {
                "id":6,
                "name":"jezik",
                "position":4,
                "visible": True,
                "variation": False,
                "options":[
                    "English"
                ]
            },
            {
                "id":1,
                "name":"uvez",
                "position":5,
                "visible": True,
                "variation": False,
                "options":[
                    st.session_state['Format']
                ]
            },
            {
                "id":12,
                "name":"ISBN",
                "position":6,
                "visible": True,
                "variation": False,
                "options":[
                    st.session_state['ISBN']
                ]
            },
            {
                "id":20,
                "name":"dimenzije",
                "position":7,
                "visible": True,
                "variation": False,
                "options":[
                    st.session_state['Dimensions']
                ]
            }
        ],

    }

    print(wcapi.post("products", data).json())
    st.text_area(data.json())

    st.text("Book named " + str( st.session_state['Title'] ) + " was imported to category " + str(st.session_state['selected_category']))



