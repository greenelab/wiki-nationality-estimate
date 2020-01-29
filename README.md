# Name-based nationality prediction

This is a data analysis repository for the study at https://greenelab.github.io/iscb-diversity-manuscript/.

## Scrape Wikipedia

Names are pulled from Wikipedia's category of Living People. 

01.get-wikipedia-pages.py navigates through the multiple pages of the category to allow access to all 900,000+ pages.

02.scrape-wikipedia.py actually navigates to individual people's pages, as linked from the living people list, and parses out name and nationality. This step is time-intensive, so parallelization is strongly recommended. This functionality is available via parallelize_wiki.sh.

03.process-wiki-output cleans the names returned in step 2 (removing nicknames, common suffixes, etc.) and maps the nationality returned in step 2 to a larger region and subsequent classifier class.

## Build classifier

04.featurize-names.py splits the names into a list of n-grams (e.g. "Jane Doe" split into 3-grams becomes the document ["Jan","ane","ne ", "e D", " Do", "Doe"]) which is use as input for the classifier. and splits the wiki data into training and evaluation sets.

05.train-evaluate-model.py builds the LSTM neural network used as a classifier on the training data created in step 4, and then returns accuracy metrics as measured on the evaluation set.

## Use classifier

06.test-ismb-data.py takes conference speaker and journal author data from https://github.com/greenelab/iscb-diversity (code to produce these data also available in that repo) and runs them through our classifier.

## License

The entire repository is released under a BSD 3-Clause License as written in [`LICENSE.md`](LICENSE.md).
In addition, the contents of the [`data`](data) and [`models`](models) directories are released under a [CC0 Public Domain Dedication](https://creativecommons.org/publicdomain/zero/1.0/).
Note that this repository contains information from [Wikipedia](https://en.wikipedia.org), which is licensed under [CC BY-SA 3.0](https://en.wikipedia.org/wiki/Wikipedia:Text_of_Creative_Commons_Attribution-ShareAlike_3.0_Unported_License).
However, our understanding is that we are reusing purely factual data from Wikipedia that is not subject to copyright in the United States.
