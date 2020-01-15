mkdir tmp


#split url list into 20 equal parts
split -n l/20 data/all_url_pages.tsv tmp/urls_

#| parallel -j5 python3 02.scrape-wikipedia.py

parallel --link -j3 python3 02.scrape-wikipedia.py --u {1} --o {2} ::: tmp/urls_a{a..t} ::: tmp/output_urls_a{a..t}

#TODO: change to wait for all scripts to finish

cat tmp/output_urls* > data/new_scraped_names.tsv
