import time
from scraper import create_db, scrape_page
from bs4 import BeautifulSoup
import requests
import re

# Create the database
db_file = 'celebration.db'
create_db(db_file, drop=True)

# Scrape the page
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0'}
url = 'https://www.eortologio.net/giortes/1'
page = requests.get(url, headers=headers)
soup = BeautifulSoup(page.content, 'html.parser')

# Extract the letters names start with
table = soup.find('table', class_='table table-bordered')
rows = table.find_all('tr')
letters = [column.text.strip() for row in rows for column in row.find_all('td')]

# Scan each page and store the data
links = soup.find_all('a', href=re.compile(r'/giortes/\d+'))

for link, letter in zip(links, letters):
    url = f"https://www.eortologio.net{link['href']}"
    scrape_page(url, headers, db_file=db_file, letter=letter)
    time.sleep(2)