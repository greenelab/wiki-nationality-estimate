import requests
from bs4 import BeautifulSoup
import re


def find_next_page(url):
    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'lxml')
    for link in soup.find_all(name='a', href=True):
        is_next_page = re.search("next page", link.text)
        if is_next_page is not None:
            new_url = "https://en.wikipedia.org" + link['href']
            return new_url
    return None


url = 'https://en.wikipedia.org/wiki/Category:Living_people'
all_links = [url]

pages_left_to_scan = True
while pages_left_to_scan:
    next_page = find_next_page(url)
    if next_page is not None:
        all_links.append(next_page)
        url = next_page
    else:
        pages_left_to_scan = False

outfile = open("data/all_url_pages.tsv", "w")
for line in all_links:
    outfile.write(line+"\n")
outfile.close()
