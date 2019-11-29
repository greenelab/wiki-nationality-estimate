import sys
import re

def process_name(name):
    #get rid of nicknames in quotes
    name=re.sub('\".*\"',"",name)
    #remove periods
    name=re.sub("\.","",name)
    ##work with or
    #almost always a name previously seen
    name=re.sub(" or simply.*","",name)
    name=re.sub(" also known as just .*","",name)
    #name=re.sub(" or .*","",name)
    #name=re.sub("also known as .*","",name)
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
    #remove common suffixes
    name=re.sub(" Jr","",name)
    name=re.sub(" Sr","",name)
    name=re.sub(" III?","",name)
    name=re.sub(" IV","",name)
    name=re.sub(" CBE","",name)
    names=name.split()

    #use number of names to ascertain which are given and family names
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

def process_nationality(country):
    if country in countries:
        return countries[country]
    else:
        return "Other"

countries={}
    
countryfile=open('country_list_annotated','r')
for line in countryfile:
    line=line.strip().split('\t')
    print(line)
    country=line[0]
    region=line[1]
    countries[country]=region

namefile=open('second_full_pass.tsv','r')
outfile=open('annotated_names.tsv','w')
outfile.write("name_first,name_middle,name_last,ethnicity\n")
for line in namefile:
    line=line.strip().split('\t')
    name=line[0]
    namelist=process_name(name)
    nationality=line[1]
    country=process_nationality(nationality)
    outfile.write(namelist+country+'\n')

outfile.close()
