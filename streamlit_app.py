from collections import namedtuple
import altair as alt
import math
import os
import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup
import requests
import time

months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
st.set_page_config(layout="wide")


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

st.text(requests.get("www.strucnaliteratura.hr/wp-json/wc/v3/products/categories?consumer_key=" + str(st.secrets["CK"]) + "&consumer_secret=" + str(st.secrets["CS"])))


with st.form("show_book_form"):
    link = st.text_input('Link', '')

    # Every form must have a submit button.
    submitted = st.form_submit_button("Submit")

    if submitted:


        book_data = wiley_scrape(link)

        st.text(link)


        col1, col2 = st.columns([4, 2])


        

        with col1: 
            while book_data is None:
                st.spinner('Wait for it...')
            if(book_data.get('Error')):
                st.warning(book_data.get('Error'))
                st.stop()
            else:
                st.success('Done!')
 
            subcol1, subcol2 = st.columns(2)

            with subcol1:
                isbn = st.text_input('ISBN', book_data.get('ISBN',''))
                title = st.text_input('Title', book_data.get('Title',''))
                subtitle = st.text_input('Subtitle', book_data.get('Subtitle',''))
                authors = st.text_input('Authors', book_data.get('Authors',''))

            with subcol2:
                year = st.text_input('Year', book_data.get('Year',''))
                pages = st.text_input('Pages', book_data.get('Pages',''))
                format = st.text_input('Format', book_data.get('Format',''))
                price = st.text_input('Price (Euro)', book_data.get('Price (Euro)',''))

            category = st.text_input('Category', book_data.get('Category',''))
            description = st.text_area('Description', book_data.get('Description',''), height= 400)   

        with col2: 
            st.image(
                book_data.get('Image URL', ''),
                use_column_width=True
            )






