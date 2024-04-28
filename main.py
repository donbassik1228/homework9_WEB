import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import json


client = MongoClient('mongodb://localhost:27017/')
db = client['quotes_db']
quotes_collection = db['quotes']
authors_collection = db['authors']


def get_page(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to retrieve page: {url}")


def parse_quotes(page_content):
    soup = BeautifulSoup(page_content, 'html.parser')
    quotes = []
    for quote in soup.find_all('div', class_='quote'):
        text = quote.find('span', class_='text').text
        author = quote.find('small', class_='author').text
        tags = [tag.text for tag in quote.find_all('a', class_='tag')]
        quotes.append({'text': text, 'author': author, 'tags': tags})
    return quotes


def parse_authors(page_content):
    soup = BeautifulSoup(page_content, 'html.parser')
    authors = []
    for author in soup.find_all('div', class_='author-details'):
        name = author.find('h3', class_='author-title').text.strip()
        birth_date = author.find('span', class_='author-born-date').text.strip()
        birth_place = author.find('span', class_='author-born-location').text.strip()
        bio = author.find('div', class_='author-description').text.strip()
        authors.append({'name': name, 'birth_date': birth_date, 'birth_place': birth_place, 'bio': bio})
    return authors


def scrape_and_load_data(url):
    
    page_content = get_page(url)
    quotes = parse_quotes(page_content)
    with open('quotes.json', 'w') as file:
        json.dump(quotes, file, indent=4)
    print('Quotes scraped and saved to quotes.json')

    
    with open('quotes.json') as file:
        quotes_data = json.load(file)
        quotes_collection.insert_many(quotes_data)
        print('Quotes loaded into MongoDB')

    
    authors = parse_authors(page_content)
    with open('authors.json', 'w') as file:
        json.dump(authors, file, indent=4)
    print('Authors scraped and saved to authors.json')

    
    with open('authors.json') as file:
        authors_data = json.load(file)
        authors_collection.insert_many(authors_data)
        print('Authors loaded into MongoDB')


url = 'http://quotes.toscrape.com'
scrape_and_load_data(url)
