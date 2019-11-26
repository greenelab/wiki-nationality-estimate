import wikipedia
import requests
from bs4 import BeautifulSoup
import time
import numpy as np
import sys
import re

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

def get_nationality(sentence):
    onecap=re.match("[A-Z][a-z]+",sentence)
    if onecap is None:
        return None
    if onecap.group(0)=="South" or onecap.group(0)=="North" or onecap.group(0)=="New":
        twocap=re.match("[A-Z][a-z]+[ -][A-Z][a-z]+",sentence)
        if twocap:
            return twocap.group(0)
    else:
        return onecap.group(0)

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
    html = requests.get(link)
    b = BeautifulSoup(html.text, 'lxml')
    #leverage first sentence
    text=b.get_text()
    text=text.split('\n')
    for line in text:
        hasborn=re.search("[Bb]orn",line)
        hasisa=re.search("is an? ",line)
        if hasborn is not None and hasisa is not None:
            startswiththis=re.search("^This ",line)
            if startswiththis is not None:
                continue
            #print(line)
            pre_parens=re.split(" ?[\[\(,]",line)
            name=re.sub(" is a.*","",pre_parens[0])
            name=re.sub(" was .*","",name)
            #print(pre_parens)
            #print(pre_parens[0])
            #if pre_parens is not None:
            #    print(pre_parens)[0]
            #if pre_parens is None:
            #     print(line)
            #pre_comma=re.sub(",.*","",line)
            post_isa=re.split(" is an? ",line)
            if len(post_isa) > 1:
                nationality=get_nationality(post_isa[1])
                if nationality:
                    outfile.write(name+"\t"+nationality+"\n")
                break #get only first sentence matching this pattern
    #for item in b.find_all('tr'):
outfile.close()
