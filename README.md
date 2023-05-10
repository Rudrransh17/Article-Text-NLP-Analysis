# Article NLP Analysis

## Overview
The project aims to analyze various articles available online using Natural Language Processing techniques. We extract features like positivity score, negativity score, polarity score, subjectivity score, average length of sentences, complex word score, fog index, average word length, and occurrence of personal pronouns from the articles. 

## Data Collection
We collected data by inputting a CSV file containing links to various articles. The project used libraries like BeautifulSoup, requests, and os to scrape and extract text from the articles.

## Libraries Used
We used the following libraries:
- nltk
- pandas
- string
- os
- re
- requests
- BeautifulSoup

We also downloaded the 'cmudict' from nltk.corpus.

## Text Preprocessing
The text was preprocessed by tokenizing and removing stop words. We also defined complex words as words that have more than 3 syllables. 

## Feature Extraction
We calculated the positivity score by counting the number of positive words from our positive word list, and negativity score by counting the number of negative words from our negative word list. Polarity and subjectivity scores were calculated using a formula of positive and negative scores. The average length of sentences, fog index, average word length, and occurrence of personal pronouns were also extracted.

## Output
The scores of all the extracted features were stored in an output file. Further details of each feature can be found in 'Text Analysis.docx'.

## Conclusion
The project provides an insight into various articles available online, and helps in understanding the sentiment and complexity of the text.
