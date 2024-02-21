import requests
import re
from bs4 import BeautifulSoup
import sqlite3

def scrape_page(url, headers, **kwargs):
    db_file = kwargs.get('db_file', 'celebration_page.db')
    letter = kwargs.get('letter', 'A')

    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    data = get_names_dates(soup, letter)
    store_data(data, db_file)

def create_db(db_file, drop=False):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    
    if drop:
        c.execute('''DROP TABLE IF EXISTS Names''')
        c.execute('''DROP TABLE IF EXISTS Date''')
        conn.commit()

    # Create a table to store the data
    c.executescript('''CREATE TABLE IF NOT EXISTS Names(
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                        name TEXT UNIQUE);

                    CREATE TABLE IF NOT EXISTS Date(
                        name_id INT, month INT, day INT, UNIQUE(name_id, month, day));''')
    conn.commit()
    conn.close()


def get_names_dates(soup, letter):    
    data = []
    rows = soup.find_all('tr')
    
    # Initialize a counter for the number of distinct names found
    count = 0 
    # Iterate through each row and extract the name and date
    for row in rows:
        cells = row.find_all('td')
        if len(cells) == 2:
            count += 1
            name_cell = cells[0]
            date_cell = cells[1]

            # Split the diminutive forms of names by comma
            names = [a_tag.text.strip() for a_tag in name_cell.find_all('a')]

            for name in names:
                dates = []
                # Extract month and day number 
                date_links = date_cell.find_all('a', href=re.compile(r'/month/\d+/day/\d+/'))
                for link in date_links:
                    match = re.search(r'/month/(\d+)/day/(\d+)/', link['href'])
                    if match:
                        month = int(match.group(1))
                        day = int(match.group(2))
                        # date = f"{month}/{day}/2024"
                        dates.append((month, day))
                data.append((name, dates))
    print(f'Found {count} distinct names starting with {letter}.')
    return data
                
def store_data(data, db_file):
    conn = sqlite3.connect(db_file)      
    c = conn.cursor()

    for name, dates in data:
        for date in dates:
            c.execute("INSERT OR IGNORE INTO Names (name) VALUES (?) ", (name,))
            c.execute('SELECT id FROM Names WHERE name = ? ', (name,))
            name_id = c.fetchone()[0]

            c.execute('INSERT OR IGNORE INTO Date (name_id, month, day) VALUES (?, ?, ?)', (name_id, date[0], date[1]) )
    conn.commit()
    conn.close()

if __name__ == "__main__":
    db_file = 'celebration_page.db'
    create_db(db_file)
    
    url = 'https://www.eortologio.net/giortes/1'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0'}

    scrape_page(url, headers, db_file=db_file)