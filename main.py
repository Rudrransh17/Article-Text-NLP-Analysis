import nltk
nltk.download('cmudict')
from nltk.corpus import cmudict
import string
import os
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
import openpyxl


# Reads the input file
df = pd.read_excel("Input.xlsx")


# Function to scrap the article and save in new file
def scrap_article(url):
    url = url
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    article_content = soup.find('div', {
                                'class': 'td-post-content'})
    if article_content is not None:
        article_content = article_content.get_text()
    else: return " "
    article_content = re.sub('<[^<]+?>', '', article_content)
    return article_content


# Function to return list of tokens which are not in stop words from the article
def get_tokens(input_text):
    tokens = nltk.word_tokenize(input_text.lower())
    filtered_tokens = [token for token in tokens if token not in stop_words]
    return filtered_tokens


# Load the CMU pronunciation dictionary
cmu_dict = cmudict.dict()
# Function to check if a word is complex
def is_complex(word):
    num_syllables = 0
    word = re.sub(r'[^a-zA-Z]', '', word)
    if word.lower() in cmu_dict:
        num_syllables = len(
            list(y for y in cmu_dict[word.lower()][0] if y[-1].isdigit()))
    return num_syllables >= 3


# Function to count the number of syllables in a word
def count_syllables(word):
    vowels = "aeiouy"
    num_vowels = 0
    prev_char = None
    for char in word:
        if char.lower() in vowels:
            if prev_char and prev_char.lower() in vowels:
                continue
            num_vowels += 1
        prev_char = char
    return num_vowels


# Goes through urls from input file and saves each article
url_id = 37
for url in df['URL']:
    article = scrap_article(url)
    with open(f"article_files/{url_id}.txt", "w", encoding="utf-8") as f:
        f.writelines(url.split('/')[-2].replace("-"," "))
        f.writelines(article)
    url_id = url_id + 1

# Stop words -->
stop_words_dir = "E:\Projects\Blackcoffer Internship Assignment\StopWords"
stop_word_files = os.listdir(stop_words_dir)
stop_words = list()

# Read the stop word files and store all stop words in a list
for file in stop_word_files:
    f = os.path.join(stop_words_dir, file)
    with open(f, 'r') as file_content:
        stop_words += file_content.readlines()
          
# Removes unnecessary characters and spaces from all stop words
for i in range(len(stop_words)):
    stop_words[i] = stop_words[i].replace('\n', '').replace(' ', '').lower()
    if '|' in stop_words[i]:
        temp = stop_words[i]
        temp = temp.split('|')
        stop_words[i] = temp[0]
        stop_words.append(temp[1])

# Positive and Negative words -->
negative_words_dir = "E:\Projects\Blackcoffer Internship Assignment\MasterDictionary\\negative-words.txt"
positive_words_dir = "E:\Projects\Blackcoffer Internship Assignment\MasterDictionary\positive-words.txt"
positive_words_list = list()
negative_words_list = list()

# Reads negative words file and store negative words in a list
with open(negative_words_dir,'r') as f:
    negative_words_list+=f.readlines()
for i in range(len(negative_words_list)):
    negative_words_list[i] = negative_words_list[i].replace('\n','').replace(' ', '').lower()
    
# Reads positive words file and store positive words in a list
with open(positive_words_dir,'r') as f:
    positive_words_list+=f.readlines()   
for i in range(len(positive_words_list)):
    positive_words_list[i] = positive_words_list[i].replace('\n','').replace(' ', '').lower()
    
    
# Store all articles in a dictionary with url id as key
id_articles_dict = dict()
articles_dir = "E:\Projects\Blackcoffer Internship Assignment\\article_files"
article_files = os.listdir(articles_dir)
for file in article_files:
    id = file[:-4]
    file = os.path.join(articles_dir, file) 
    with open(file, 'r',encoding = "utf-8") as f:
        article = f.read()
    id_articles_dict[id] = article
    
    
# Store tokens and token count in seperate dictionary with url id as key 
id_tokens_dict = dict()
token_count_dict = dict()
for id, article in id_articles_dict.items():
    id_tokens_dict[id] = get_tokens(article)
    token_count_dict[id] = len(id_tokens_dict[id])
    

# Find positive score of each article and store in dictionary with url id as key
positive_score_dict = dict()
for id, tokens in id_tokens_dict.items():
    positive_score_dict[id] = 0
    for token in tokens:
        if token in positive_words_list:
            positive_score_dict[id] +=1
            
         
# Find negative score of each article and store in dictionary with url id as key
negative_score_dict = dict()
for id, tokens in id_tokens_dict.items():
    negative_score_dict[id] = 0
    for token in tokens:
        if token in negative_words_list:
            negative_score_dict[id] +=1
       
            
# Find polarity and subjectivity score and story in dictionary with url id as key         
polarity_score_dict = dict()
subjectivity_score_dict = dict()
for id in id_tokens_dict.keys():
    p = positive_score_dict[id]
    n = negative_score_dict[id]
    total = len(id_tokens_dict[id])
    polarity_score_dict[id] = (p-n)/(p+n+0.000001)
    subjectivity_score_dict[id] = (p+n)/(total+0.000001)


# Find average length of sentence and story in dictionary with url id as key
avg_sentence_length_dict = dict()
tokenizer = nltk.tokenize.sent_tokenize
for id, article in id_articles_dict.items():
    sentences = tokenizer(article)
    sen_count = len(sentences)
    words = len(article.split())
    avg_sentence_length_dict[id] = words/sen_count


# Find complex word count and percent and store in seperate dictionary with url id as key
complex_word_percent_dict = dict()
complex_word_count_dict = dict()
for id, article in id_articles_dict.items():
    words = article.split()
    complex_words = [word for word in words if is_complex(word)]
    num_complex_words = len(complex_words)
    complex_word_count_dict[id] = num_complex_words
    complex_word_percent_dict[id] = num_complex_words*100/len(words)


# Calculate fog index and store in dictionary with url id as key
fog_index_dict = dict()
for id, article in id_articles_dict.items():
    fog_index_dict[id] = 0.4 * \
        (avg_sentence_length_dict[id] + complex_word_percent_dict[id])


# Average words per sentence is same as average sentence length
avg_words_per_sentence = avg_sentence_length_dict


# Find average syllables per word and store in dictionary with url id as key
syllable_count_per_word = dict()
for id, article in id_articles_dict.items():
    words = article.split()
    num_syllables = 0
    for word in words:
        num_syllables = sum(count_syllables(word) for word in words)
    syllable_count_per_word[id] = num_syllables/len(words)


# Define the personal pronouns
personal_pronouns = ['I', 'we', 'my', 'ours', 'us', 'My', 'We', 'Ours', 'Us']
# Count the total number of occurence of these pronouns and store in a dictionary
pronoun_count = dict()
for id, article in id_articles_dict.items():
    words = article.split()
    counts = {word: words.count(word) for word in personal_pronouns}
    pronoun_count[id] = sum(counts.values())
    
    
# Find the average word length and store in dictionary with url id as key
avg_word_length = dict()
for id, article in id_articles_dict.items():
    words = article.split()
    total_characters = sum(len(word) for word in words)
    total_words = len(words)
    avg_word_length[id] = total_characters / total_words


# Make a new dataframe for output and copy url_id and url from input file
output_df = pd.DataFrame()
output_df['URL_ID'] = df['URL_ID']
output_df['URL'] = df['URL']

# Write the values of all variables using the dictionaries.
i=0
for url in output_df['URL_ID']:
    output_df.loc[i,'POSITIVE SCORE'] = positive_score_dict[str(url)]
    output_df.loc[i,'NEGATIVE SCORE'] = negative_score_dict[str(url)]
    output_df.loc[i,'POLARITY SCORE'] = polarity_score_dict[str(url)]
    output_df.loc[i,'SUBJECTIVITY SCORE'] = subjectivity_score_dict[str(url)]
    output_df.loc[i,'AVG SENTENCE LENGTH'] = avg_sentence_length_dict[str(url)]
    output_df.loc[i,'PERCENTAGE OF COMPLEX WORDS'] = complex_word_percent_dict[str(url)]
    output_df.loc[i,'FOG INDEX'] = fog_index_dict[str(url)]
    output_df.loc[i,'AVG NUMBER OF WORDS PER SENTENCE'] = avg_words_per_sentence[str(url)]
    output_df.loc[i,'COMPLEX WORD COUNT'] = complex_word_count_dict[str(url)]
    output_df.loc[i,'WORD COUNT'] = token_count_dict[str(url)]
    output_df.loc[i,'SYLLABLE PER WORD'] = syllable_count_per_word[str(url)]
    output_df.loc[i,'PERSONAL PRONOUNS'] = pronoun_count[str(url)]
    output_df.loc[i,'AVG WORD LENGTH'] = avg_word_length[str(url)]
    i+=1
    
# Saves the output file
output_df.to_excel("output.xlsx")
