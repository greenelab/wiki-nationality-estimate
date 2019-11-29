import wikipedia
import requests
from bs4 import BeautifulSoup
#import pycountry
import time
import numpy as np
import sys
import re

countries=[]
with open('country_list','r') as f:
    for line in f:
        line=line.strip()
        countries.append(line)

def link_check(link):
    is_wiki=re.search("^\/wiki\/",link)
    if is_wiki is None:
        return False
    is_category=re.search("\/wiki\/Category",link)
    if is_category is not None:
        return False
    is_wiki2=re.search("\/wiki\/Wikipedia",link)
    if is_wiki2 is not None:
        return False
    is_special=re.search("\/wiki\/Special",link)
    if is_special is not None:
        return False
    is_portal=re.search("\/wiki\/Portal",link)
    if is_portal is not None:
        return False
    is_main=re.search("\/wiki\/Main_Page",link)
    if is_main is not None:
        return False
    is_help=re.search("\/wiki\/Help:",link)
    if is_help is not None:
        return False
    is_template=re.search("\/wiki\/Template:",link)
    if is_template is not None:
        return False
    return True

'''def get_nationality(sentence):
    onecap=re.match("[A-Z][a-z]+",sentence)
    if onecap is None:
        return None
    if onecap.group(0)=="South" or onecap.group(0)=="North" or onecap.group(0)=="New":
        twocap=re.match("[A-Z][a-z]+[ -][A-Z][a-z]+",sentence)
        if twocap:
            return twocap.group(0)
    else:
        return onecap.group(0)
'''
def get_nationality(sentence):
    for country in countries:
        if re.match(country,sentence) is not None:
            return country
    return ""

def is_words(match):
    propernoun=re.match("[A-Z][a-z]+",match)
    if propernoun is None:
        return False
    else:
        return True

#TODO switch to argparse
urllist=open(sys.argv[1],'r')
outfile=open(sys.argv[2],'w')

links=[]
for line in urllist:
    line=line.strip()
    html = requests.get(line)
    soup = BeautifulSoup(html.text, 'lxml')
    for i in soup.find_all(name = 'li'):
        # pull the actual link for each one
        for link in i.find_all('a', href=True):
            if link_check(link['href']):
                links.append(link['href'])

print(len(links))
full_links = ['https://en.wikipedia.org'+ i for i in links]

for link in full_links:
    #outfile.write(link+'\n')
    sentence_name=""
    tr_name=""
    sentence_nationality=""
    tr_nationality=""
    passed_bornisa=False
    hit_startswiththis=False
    passed_isa=False
    passed_nationality=False
    html = requests.get(link)
    b = BeautifulSoup(html.text, 'lxml')
    #leverage first sentence
    text=b.get_text()
    text=text.split('\n')
    for line in text:
        hasborn=re.search("[Bb]orn",line)
        hasisa=re.search("is an? ",line)
        #if hasisa is not None:
        if hasborn is not None and hasisa is not None:
            passed_bornisa=True
            startswiththis=re.search("^This ",line)
            if startswiththis is not None:
                hit_startswiththis=True
                continue
            #print(line)
            pre_parens=re.split(" ?[\[\(,]",line)
            name=re.sub(" is a.*","",pre_parens[0])
            name=re.sub(" was .*","",name)
            name=re.sub(" or .*","",name)
            name=re.sub("also known as .*","",name)
            sentence_name=name
            #print(pre_parens)
            #print(pre_parens[0])
            #if pre_parens is not None:
            #    print(pre_parens)[0]
            #if pre_parens is None:
            #     print(line)
            #pre_comma=re.sub(",.*","",line)
            post_isa=re.split(" is an? ",line)
            if len(post_isa) > 1:
                passed_isa=True
                nationality=get_nationality(post_isa[1])
                if nationality:
                    passed_nationality=True
                    #outfile.write(name+"\t"+nationality+"\n")
                    sentence_nationality=nationality
                #else:
                    #outfile.write("Unable to find nationality\n")
                #break #get only first sentence matching this pattern
    '''if passed_bornisa==False:
        outfile.write("No line with 'born' and 'is a'\n")
    elif hit_startswiththis:
        outfile.write("Born and 'is a' line started with 'this'\n")
    elif passed_isa==False:
        outfile.write("No content after 'is a'\n")
    elif passed_nationality==False:
        outfile.write("No proper noun found after 'is a'\n")'''
            
    for item in b.find_all('tr'):
        itemstring=str(item)
        if re.search('[Bb]irthplace',itemstring) is not None or re.search('[Bb]orn',itemstring) is not None or re.search('[Nn]ationality',itemstring) is not None or re.search('[Nn]ickname',itemstring) is not None:
            #print(itemstring)
            #print("############")
            #s=item.find_all(text=True)
            tr_nationality=get_nationality(itemstring)
            #outfile.write(persons_name+"\t"+s[-1]+'\n')
            #print(s[-1])
            #for child in item.children:
            #    print(child)
            #sys.exit()
            #print(item.children)
        if re.search("class=[\"\'][Nn]ickname[\"\']",itemstring) is not None:
            for child in item.children:
                if re.search("class=[\"\'][Nn]ickname[\"\']",str(child)) is not None:
                    s=child.find_all(text=True)
                    if len(s)>=1:
                        tr_name=s[-1].strip()
    sentence_words=is_words(sentence_name)
    tr_words=is_words(tr_name)
    if sentence_words and not tr_words:
        persons_name=sentence_name
    elif tr_words and not sentence_words:
        persons_name=tr_name
    elif tr_words and sentence_words:
        #outfile.write("pick between "+tr_name+'\t'+sentence_name+'\n')
        persons_name=sentence_name
    else:
        continue
    sentence_words=is_words(sentence_nationality)
    tr_words=is_words(tr_nationality)
    if sentence_words and not tr_words:
        persons_nationality=sentence_nationality
    elif tr_words and not sentence_words:
        persons_nationality=tr_nationality
    elif tr_words and sentence_words:
        #outfile.write("pick between "+tr_nationality+'\t'+sentence_nationality+'\n')
        persons_nationality=tr_nationality
    else:
        continue
    outfile.write(persons_name+"\t"+persons_nationality+'\n') 
#TODO: write or find some sort of nationality recognizing function 
outfile.close()
