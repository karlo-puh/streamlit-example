from collections import namedtuple
import altair as alt
import math
import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup
import requests
import re


def wiley_scrape(url):
    try:
        page = requests.get(url)
        page.raise_for_status()
        soup = BeautifulSoup(page.content, 'html.parser')
        
        description = soup.find('div', class_='description')
        authors = ', '.join(a.text.strip() for a in soup.find_all('a', class_='product-authors'))
        year, pages = '', ''
        
        for p in soup.select('.product-summary p'):
            if p.text.startswith('ISBN'):
                isbn = p.find_next_sibling('p').text
            elif p.text.startswith('Published:'):
                year = p.find_next_sibling('p').text.split()[-1]
            elif p.text.startswith('Pages:'):
                pages = p.find_previous_sibling('p').text.split()[-1]
        
        image_url = soup.find('div', class_='item-image').find('img')['src']
        
        return {
            'Image URL': image_url,
            'Description': description.text.strip(),
            'Authors': authors,
            'Year': year,
            'Pages': pages
        }
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

"""

# Book Import
"""

link = st.text_input('Zalijepite link knjige', 'https://www...')

if st.button("Pretraži", type="primary"):
    st.write('Tražim knjigu na linku', link)
    scraped_info = wiley_scrape(link)

    

if scraped_info:
    for key, value in scraped_info.items():
        st.text(f"{key}: {value}")



