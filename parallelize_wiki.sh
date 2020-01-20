mkdir tmp

# Split url list into 20 equal parts
split -n l/20 data/all_url_pages.tsv tmp/urls_

# Process url chunks in parallel, 3 at a time (more causes 'connection refused' issues)
parallel --link -j3 python3 02.scrape-wikipedia.py --u {1} --o {2} ::: tmp/urls_a{a..t} ::: tmp/output_urls_a{a..t}

cat tmp/output_urls* > data/scraped_names.tsv
