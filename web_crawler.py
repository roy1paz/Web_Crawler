import time
import json
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from sql_utils import *

POSITIONS_DATA_DIR = 'positions_data'


def read_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


def create_data_dir():
    if not os.path.exists(POSITIONS_DATA_DIR):
        os.makedirs(POSITIONS_DATA_DIR)


def initialize_webpage_scraper(url):
    response = requests.get(url)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    if response.status_code == 200:
        # Initialize a Chrome WebDriver instance
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get(url)  # Open the webpage
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        return soup, driver
    else:
        raise Exception(f'request error, code: {response.status_code}')


def get_position_data(li):
    a_tag = li.find('a')
    href = a_tag.get('href')
    position_name = a_tag.find('h2').get_text()
    location_element = a_tag.find(class_='job-location-search').get_text().split(',')
    city = location_element[0]
    county = location_element[0] if len(location_element) == 1 else location_element[1][2:]
    position = {'name': position_name,
                'country': county,
                'city': city,
                'href': href,
                }
    return position


def get_position_description(url):
    soup, driver = initialize_webpage_scraper(url)
    description = soup.find(class_='ats-description').get_text(separator='\n', strip=True).replace('\n', ' ')
    return description


def write_json(position_data, index):
    file_path = os.path.join(POSITIONS_DATA_DIR, f'position_{index}.json')
    with open(file_path, 'w', encoding="utf-8") as json_file:
        json.dump(position_data, json_file, indent=4, ensure_ascii=False)


def write_positions(positions):
    for i, pos in enumerate(positions):
        write_json(pos, i + 1)  # position data to json


def valid_next_page(current_next_href, next_button_href):
    if current_next_href == next_button_href:   # if last page - stop
        return False
    return True


def click_next_page(driver, next_button, current_next_href):
    next_button_href = next_button.get_attribute('href')
    next_page = valid_next_page(current_next_href, next_button_href)
    current_next_href = next_button_href
    next_button.click()
    driver.refresh()
    time.sleep(2)
    return next_page, current_next_href


def web_scraping():
    url = 'https://jobs.dell.com/search-jobs'
    soup, driver = initialize_webpage_scraper(url)
    current_next_href = 'https://jobs.dell.com/search-jobs/results&p=1'
    next_page = True
    positions = []

    while next_page:
        # Find the position table
        search_results_section = soup.find('section', {'id': 'search-results-list'})
        if search_results_section:
            list_items = search_results_section.find_all('li')  # find all li in the table
            for i in range(len(list_items)):
                position = get_position_data(list_items[i])
                positions.append(position)
        else:
            break
        # click next page
        next_button = WebDriverWait(driver, 20).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '.pagination-paging .next')))
        next_page, current_next_href = click_next_page(driver, next_button, current_next_href)
        # update soup source
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

    # get job description
    for i in range(len(positions)):
        desc_url = 'https://jobs.dell.com' + positions[i]['href']
        del positions[i]['href']
        positions[i]['description'] = get_position_description(desc_url)
    # Close the WebDriver instance
    driver.quit()
    return positions


if __name__ == '__main__':
    create_data_dir()   # create dict
    positions_data = web_scraping()  # get data from web
    write_positions(positions_data)
    create_db()
    create_table()
    insert_into_mysql(POSITIONS_DATA_DIR)   # insert all files to mysql db
