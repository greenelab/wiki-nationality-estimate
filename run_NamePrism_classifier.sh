python3 03.process-wiki-output.py -c data/country_to_region_NamePrism.tsv -o data/annotated_names_NamePrism.tsv
python3 04.featurize-names.py -n data/annotated_names_NamePrism.tsv -m NamePrism
python3 05.train-model.py -n data/annotated_names_NamePrism.tsv -m NamePrism
python3 06.evaluate-model.py -n data/annotated_names_NamePrism.tsv -m NamePrism
python3 07.test-ismb-data.py -m NamePrism
