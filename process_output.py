import sys
import re
import pandas
import argparse

def process_name(name):
    #get rid of nicknames in quotes
    name=re.sub('\".*\"',"",name)
    #remove content between forward slashes, usually name pronunciations
    name=re.sub(' /.*/ ',"",name)

    #remove periods
    name=re.sub("\.","",name)
    name=re.sub(",","",name)
    
    #almost always a name previously seen
    name=re.sub(" or simply.*","",name)
    name=re.sub(" also known as just .*","",name)
    
    #split on 'or'/'also known as' and process longer name
    two_names=name.split(" also known as ")
    if len(two_names)>1:
        if len(two_names[0])>=len(two_names[1]):
            name=two_names[0]
        else:
            name=two_names[1]
    two_names=name.split(" or ")
    if len(two_names)>1:
        if len(two_names[0])>=len(two_names[1]):
            name=two_names[0]
        else:
            name=two_names[1]
    two_names=name.split(" also ")
    if len(two_names)>1:
        if len(two_names[0])>=len(two_names[1]):
            name=two_names[0]
        else:
            name=two_names[1]
    two_names=name.split(" [a-z]\+ known as ")
    if len(two_names)>1:
        if len(two_names[0])>=len(two_names[1]):
            name=two_names[0]
        else:
            name=two_names[1]


    #remove common suffixes
    name=re.sub(" Jr","",name)
    name=re.sub(" Sr","",name)
    name=re.sub(" III?","",name)
    name=re.sub(" IV","",name)
    name=re.sub(" CBE","",name)
    name=re.sub(" OBE","",name)
    name=re.sub(" MBE","",name)

    #remove common prefixes
    name=re.sub("Sir ","",name)
    name=re.sub("Dame ","",name)
    name=re.sub("Dr.? ","",name)

    #throw out any name containing one or more of these characters
    bad_chars = ['!', '“', '%', '&', '\(', '\)', '\/',':', ';', '=', '\?', '@','\]','\[', '_', '`','{', '\|', '}', '~','[0-9]']
    for char in bad_chars:
        if re.search(char,name) is not None:
            return None

    #use number of names to ascertain which are given and family names
    names=name.split()
    if len(names)==1:
        string=names[0]+",,,"
        return(string)
    if len(names)==2:
        string=names[0]+",,"+names[1]+","
        return(string)
    if len(names)==3:
        string=names[0]+","+names[1]+","+names[2]+","
        return(string)
    if len(names)>3:
        string=names[0]+","+" ".join(names[1:len(names)-1])+","+names[len(names)-1]+","
        return string

def process_nationality(nationality):
    try:
        country=countries[nationality]
    except:
        return None
    try:
        return regions[country]
    except:
        return None

parser = argparse.ArgumentParser()
parser.add_argument("-e","--ethnicolr",action="store_true")
args = parser.parse_args()

countries={}
regions={}

countryfile=open('nationality_to_country.txt','r')
for line in countryfile:
    line=line.strip().split('\t')
    nationality=line[0]
    country=line[1]
    countries[nationality]=country

regionfile=open("country_to_region.txt",'r')
for line in regionfile:
    line=line.strip().split('\t')
    country=line[0]
    if args.ethnicolr:
        regions[country]=line[3]
    else:
        regions[country]=line[2]

namefile=open('third_full_pass.tsv','r')
if args.ethnicolr:
    ofile='annotated_names_ethnicolr.tsv'
else:
    ofile='annotated_names.tsv'

outfile=open(ofile,'w')
outfile.write("id,name_first,name_middle,name_last,ethnicity\n")
for line in namefile:
    line=line.strip().split('\t')
    num=line[0]
    name=line[1]
    namelist=process_name(name)
    if namelist is None:
        continue
    nationality=line[2]
    country=process_nationality(nationality)
    if country is None:
        continue
    outfile.write(num+","+namelist+'\"'+country+'\"\n')

outfile.close()
