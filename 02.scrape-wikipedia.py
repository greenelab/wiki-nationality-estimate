import re
import requests
import argparse
from bs4 import BeautifulSoup


def link_check(link):
    #  Each page of the wikipedia Category:Living_people has
    #  many links, some of which are to our persons of interest
    #  and some of which are to other wikipedia pages (e.g. the
    #  main page, the help section) This function should return
    #  true only for the links of the 200-or-so person pages.
    is_wiki = re.search("^\/wiki\/", link)
    if is_wiki is None:
        return False
    is_category = re.search("\/wiki\/Category", link)
    if is_category is not None:
        return False
    is_wiki2 = re.search("\/wiki\/Wikipedia", link)
    if is_wiki2 is not None:
        return False
    is_special = re.search("\/wiki\/Special", link)
    if is_special is not None:
        return False
    is_portal = re.search("\/wiki\/Portal", link)
    if is_portal is not None:
        return False
    is_main = re.search("\/wiki\/Main_Page", link)
    if is_main is not None:
        return False
    is_help = re.search("\/wiki\/Help:", link)
    if is_help is not None:
        return False
    is_template = re.search("\/wiki\/Template:", link)
    if is_template is not None:
        return False
    return True


def get_nationality(sentence):
    #  Search for a country name in text. The country file should be ordered
    #  such that countries that are a partial name of another country come
    #  afterward (e.g. the algorithm checks for a match of Equitorial Guinea
    #  before checking for a match of Guinea)
    for country in countries:
        if re.match(country, sentence) is not None:
            return country
    for country in countries:
        if re.search(country, sentence) is not None:
            return country
    return ""


def is_words(match):
    #  Ensure that a name found is a proper noun, presumed to begin with a
    #  capital letter.
    propernoun = re.search("[A-Z][a-z]+", match)
    if propernoun is None:
        return False
    else:
        return True


p = argparse.ArgumentParser()
p.add_argument("-u", "--urllist", default="data/all_url_pages.tsv")
p.add_argument("-o", "--outfile", default="data/scraped_names.tsv")
p.add_argument("-c", "--countrylist", default="data/demonyms.tsv")
args = p.parse_args()

countries = []
with open(args.countrylist, 'r') as f:
    for line in f:
        line = line.strip()
        countries.append(line)

print("---- Loading urls for",args.urllist,"----")

links = []
with open(args.urllist, 'r') as u:
    for line in u:
        line = line.strip()
        html = requests.get(line)
        soup = BeautifulSoup(html.text, 'lxml')
        for link in soup.find_all(name='a', href=True):
            #  pull the actual link for each one
            if link_check(link['href']):
                links.append(link['href'])

print("---- Loaded",len(links),"pages from",args.urllist,"----")

full_links = ['https://en.wikipedia.org' + i for i in links]

name_id = 1
outfile = open(args.outfile, "w")
for link in full_links:
    # outfile.write(link+'\n')
    sentence_name = ""
    tr_name = ""
    sentence_nationality = ""
    tr_nationality = ""
    passed_bornisa = False
    hit_startswiththis = False
    passed_isa = False
    passed_nationality = False
    html = requests.get(link)
    b = BeautifulSoup(html.text, 'lxml')
    # leverage first sentence
    text = b.get_text()
    text = text.split('\n')
    for line in text:
        hasborn = re.search("[Bb]orn", line)
        hasisa = re.search("is an? ", line)
        if hasborn is not None and hasisa is not None:
            passed_bornisa = True
            startswiththis = re.search("^This ", line)
            if startswiththis is not None:
                hit_startswiththis = True
                continue
            # print(line)
            pre_parens = re.split(" ?[\[\(,]", line)
            name = re.sub(" is a.*", "", pre_parens[0])
            name = re.sub(" was .*", "", name)
            name = re.sub(" or .*", "", name)
            name = re.sub("also known as .*", "", name)
            sentence_name = name
            post_isa = re.split(" is an? ", line)
            if len(post_isa) > 1:
                passed_isa = True
                nationality = get_nationality(post_isa[1])
                if nationality:
                    passed_nationality = True
                    sentence_nationality = nationality
                    break
            
    for item in b.find_all('tr'):
        itemstring = str(item)
        if re.search('[Bb]irthplace', itemstring) is not None or re.search('[Bb]orn', itemstring) is not None or re.search('[Nn]ationality', itemstring) is not None or re.search('[Nn]ickname', itemstring) is not None:
            tr_nationality = get_nationality(itemstring)
        if re.search("class = [\"\'][Nn]ickname[\"\']", itemstring) is not None:
            for child in item.children:
                if re.search("class = [\"\'][Nn]ickname[\"\']", str(child)) is not None:
                    s = child.find_all(text=True)
                    if len(s) == 1:
                        tr_name = s[0].strip()
                    elif len(s)>1:
                        if s[0] == '\n':
                            tr_name = s[1].strip()
                        else:
                            tr_name = s[0].strip()
    sentence_words = is_words(sentence_name)
    tr_words = is_words(tr_name)
    if sentence_words and not tr_words:
        persons_name = sentence_name
    elif tr_words and not sentence_words:
        persons_name = tr_name
    elif tr_words and sentence_words:
        # outfile.write("pick between "+tr_name+'\t'+sentence_name+'\n')
        persons_name = sentence_name
    else:
        continue
    sentence_words = is_words(sentence_nationality)
    tr_words = is_words(tr_nationality)
    if sentence_words and not tr_words:
        persons_nationality = sentence_nationality
    elif tr_words and not sentence_words:
        persons_nationality = tr_nationality
    elif tr_words and sentence_words:
        # outfile.write("pick between "+tr_nationality+'\t'+sentence_nationality+'\n')
        persons_nationality = sentence_nationality
    else:
        continue
    outfile.write(str(name_id)+"\t"+persons_name+"\t"+persons_nationality+'\n')
    name_id += 1 
outfile.close()
