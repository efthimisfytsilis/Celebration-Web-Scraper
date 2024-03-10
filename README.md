# Name Celebration Scraper
With web scraping the entire internet becomes your database. :spider:

## Introduction
This project entails an application with a GUI designed to retrieve information from a web-scraped database. The scraper extracts greek names and their associated celebration dates from [eortologio.net](https://www.eortologio.net/) and stores them in a SQLite database. The application, built using Tkinter, provides users with intuitive tabs for accessing and interacting with the collected data.

## Overview
Below is an outline of the main files included in the repository:
- [`celebration.db`](celebration.db): Stores the collected names and their associated celebration dates, serving as the repository for the scraped data. 
- [`scraper.py`](scraper.py): Extracts data from a single page of the designated source and populates the `celebration.db` database with the collected information.
- [`main.py`](main.py): Orchestrates the scraping process by executing the `scraper.py` logic across multiple pages of the target website, ensuring comprehensive data retrieval and storage.
- [`app.py`](app.py): The GUI implementation using Tkinter.

## Usage
Upon running the application, the GUI will open, providing two tabs for different functionalities:

- **Search Tab**: 
    - Loads the entire database, allowing users to view and edit (locally) the names and their corresponding celebration dates.
    - Allows users to search for a name and displays its corresponding celebration date.

- **Load File Tab**:
    - Enables users to upload tabular data with a 'name' column as a requirement and retrieves celebration dates for the included names.
    - Users can edit existing entries, add new names and dates, or delete rows as needed to customize the data.
    - Finally, once the necessary modifications have been made, users can export the file with the updated data.

## Setting Up
```
git clone https://github.com/efthimisfytsilis/Etiquette-Web-Scraper.git
```
```
pip install beautifulsoup4 customtkinter requests
```