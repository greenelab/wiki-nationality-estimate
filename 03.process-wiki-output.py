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

    # remove non-name parts
    name = re.sub(" is .*", "", name)
    name = re.sub(" who .*", "", name)

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
    bad_chars = ['!', '"', '%', '&', '\(', '\)', '\/', ':', ';', '=', '\?', '@', '\]', '\[', '_', '`', '{', '\|', '}', '~', '[0-9]']
    for char in bad_chars:
        if re.search(char, name) is not None:
            return None

    return name


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
parser.add_argument("-c", "--countryfile", default="data/country_to_region.tsv")
parser.add_argument("-o", "--outfile", default="data/annotated_names.tsv")
parser.add_argument("-s", "--sep", default="\t")
args = parser.parse_args()

countries = {}
regions = {}

countryfile = open('data/nationality_to_country.tsv', 'r')
for line in countryfile:
    line = line.strip().split('\t')
    nationality = line[0]
    country = line[1]
    countries[nationality] = country

regionfile = open(args.countryfile, 'r')
for line in regionfile:
    line = line.strip().split('\t')
    country = line[0]
    regions[country] = line[2]

namefile = open(args.names, 'r')
outfile = open(args.outfile, 'w')
outfile.write("id"+args.sep+"name"+args.sep+"ethnicity"+args.sep+"country\n")

num = 0
with open(args.names, 'r') as f:
    for line in namefile:
        line = line.strip().split('\t')
        name = line[0]
        name = process_name(name)
        if name is None:
            continue
        #first, middle, last = separate_name_parts(namelist)
        nationality = line[1]
        country, nationname = process_nationality(nationality)
        if country is None or nationname is None:
            continue
        num += 1
        outfile.write(str(num)+args.sep+name+args.sep+country+args.sep+nationname+"\n")
        #outfile.write(str(num)+args.sep+first+args.sep+middle+args.sep+last+args.sep+country+args.sep+nationname+"\n")
outfile.close()
