import sys
import re
import pandas
import argparse

def process_name(name):
    # get rid of nicknames in quotes
    name = re.sub('\".*\"', "", name)
    # remove content between forward slashes, usually name pronunciations
    name = re.sub(' /.*/ ', "", name)

    # remove periods
    name = re.sub("\.", "", name)
    name = re.sub(",", "", name)
    
    # almost always a name previously seen
    name = re.sub(" or simply.*", "", name)
    name = re.sub(" also known as just .*", "", name)
    
    # split on 'or'/'also known as' and process longer name
    two_names = name.split(" also known as ")
    if len(two_names) > 1:
        if len(two_names[0]) >= len(two_names[1]):
            name = two_names[0]
        else:
            name = two_names[1]
    two_names = name.split(" or ")
    if len(two_names) > 1:
        if len(two_names[0]) >= len(two_names[1]):
            name = two_names[0]
        else:
            name = two_names[1]
    two_names = name.split(" also ")
    if len(two_names) > 1:
        if len(two_names[0]) >= len(two_names[1]):
            name = two_names[0]
        else:
            name = two_names[1]
    two_names = name.split(" [a-z]\+ known as ")
    if len(two_names) > 1:
        if len(two_names[0]) >= len(two_names[1]):
            name = two_names[0]
        else:
            name = two_names[1]

    # TODO: look for more suffixes
    # remove common suffixes
    name = re.sub(" Jr", "", name)
    name = re.sub(" Sr", "", name)
    name = re.sub(" III?", "", name)
    name = re.sub(" IV", "", name)
    name = re.sub(" CBE", "", name)
    name = re.sub(" OBE", "", name)
    name = re.sub(" MBE", "", name)

    # remove common prefixes
    name = re.sub("Sir ", "", name)
    name = re.sub("Dame ", "", name)
    name = re.sub("Dr.? ", "", name)

    # throw out any name containing one or more of these characters
    bad_chars = ['!', '“', '%', '&', '\(', '\)', '\/', ':', ';', ' = ', '\?', '@', '\]', '\[', '_', '`', '{', '\|', '}', '~', '[0-9]']
    for char in bad_chars:
        if re.search(char, name) is not None:
            return None

    names = name.split()
    
    # remove initials
    to_remove = []
    for i in range(len(names)):
        if len(names[i]) < 2:
            to_remove.append(i)
    if len(to_remove) > 0:
        names = [element for i, element in enumerate(names) if i not in to_remove]
        
    # use number of names to ascertain which are given and family names
    if len(names) == 1:
        string = names[0]+args.sep+args.sep+args.sep
        return(string)
    if len(names) == 2:
        string = names[0]+args.sep+args.sep+names[1]+args.sep
        return(string)
    if len(names) == 3:
        string = names[0]+args.sep+names[1]+args.sep+names[2]+args.sep
        return(string)
    if len(names) > 3:
        string = names[0]+args.sep+" ".join(names[1:len(names)-1])+args.sep+names[len(names)-1]+args.sep
        return string


def process_nationality(nationality):
    try:
        country = countries[nationality]
    except:
        return None, None
    try:
        return regions[country], country
    except:
        return None, None


parser = argparse.ArgumentParser()
parser.add_argument("-n", "--names", default="data/scraped_names.tsv")
parser.add_argument("-c", "--countryfile", default="data/country_to_region.txt")
parser.add_argument("-o", "--outfile", default="data/annotated_names.tsv")
parser.add_argument("-s", "--sep", default="\t")
args = parser.parse_args()

countries = {}
regions = {}

countryfile = open('nationality_to_country.txt', 'r')
for line in countryfile:
    line = line.strip().split('\t')
    nationality = line[0]
    country = line[1]
    countries[nationality] = country

regionfile = open(args.countryfile, 'r')
for line in regionfile:
    line = line.strip().split('\t')
    country = line[0]
    regions[country] = line[2]  ##TODO: change back?

namefile = open(args.names, 'r')
outfile = open(args.outfile, 'w')
outfile.write("id"+args.sep+"name_first"+args.sep+"name_middle"+args.sep+"name_last"+args.sep+"ethnicity"+args.sep+"country\n")

with open(args.names, 'r') as f:
    for line in namefile:
        line = line.strip().split('\t')
        num = line[0]
        name = line[1]
        namelist = process_name(name)
        if namelist is None:
            continue
        nationality = line[2]
        country, nationname = process_nationality(nationality)
        if country is None or nationname is None:
            continue
        # outfile.write(num+args.sep+namelist+'\"'+country+'\"\n')
        outfile.write(num+args.sep+namelist+'\"'+country+'\"'+args.sep+nationname+"\n")

outfile.close()