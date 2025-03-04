import nltk
import re
import jieba
from nltk.tokenize import WordPunctTokenizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

sen_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle') 

# nltk.download('stopwords')

def tokenize_en(text):
    return [tok for tok in nltk.word_tokenize(text)]

# split paragraph texts in to single words
def split_para(text):
    stop_words = set(stopwords.words('english'))
    words = []
    for i, w in enumerate(tokenize_en(text)):
        if w.isalnum() and w.lower() not in stop_words:
            words.append({
                'id': i,
                'word': w,
                'stopword': False,
                'keyword': 0
            })
        else:
            words.append({
                'id': i,
                'word': w,
                'stopword': True,
                'keyword': 0
            })
    return words

def load_stopwords(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        stopwords = file.read().splitlines()
    return stopwords


def split_para_CN(text):
    stopwords_filepath = 'stopwords-zh.txt'
    stop_words = load_stopwords(stopwords_filepath)
    words = []
    for i, w in enumerate(jieba.lcut(text)):
        if w not in stop_words:
            words.append({
                'id': i,
                'word': w,
                'stopword': False,
                'keyword': 0
            })
        else:
            words.append({
                'id': i,
                'word': w,
                'stopword': True,
                'keyword': 0
            })
    return words

def split_sentence(text):
    return sen_tokenizer.tokenize(text) 

def split_CN_sentences(text):
    text = re.sub('([。！？\?])([^’”])',r'\1\n\2',text) #普通断句符号且后面没有引号
    text = re.sub('(\.{6})([^’”])',r'\1\n\2',text) #英文省略号且后面没有引号
    text = re.sub('(\…{2})([^’”])',r'\1\n\2',text) #中文省略号且后面没有引号
    text = re.sub('([.。！？\?\.{6}\…{2}][’”])([^’”])',r'\1\n\2',text) #断句号+引号且后面没有引号
    text = re.sub('([———])([^’”———])', r'\1\n\2', text)  #破折号且后面没有引号
    return text.split("\n")
