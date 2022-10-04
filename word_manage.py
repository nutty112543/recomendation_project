
from pythainlp.corpus import thai_stopwords
from pythainlp.tokenize import word_tokenize
from pythainlp.corpus.common import thai_words
from pythainlp.util import Trie

def remove_stopword(doct_text):
    stopwords = list(thai_stopwords())
    #print(stopwords)
    stopword=[]
    for word in doct_text:
        if word not in stopwords:
              stopword.append(word)
    return stopword 

def get_token_list(doc_text):
    tokens = word_tokenize(doc_text,custom_dict=new_word_dict()) 
    return tokens

def new_word_dict():
    words = ["ผิวมัน","ผิวแห้ง","ผิวผสม","ผิวปกติ","มอยซ์เจอไรเซอร์","เซรั่ม","เอสเซนส์","กันแดด","โลชั่น","โทนเนอร์","แอมพูล","มากส์","คลีนซิ่ง","ออยล์","อิมัลชั่น","ทรีทเมนท์",' ลิปบาล์ม','คลีนเซอร์','บิวตี้',"ออแกนิค",'ชีท','สลีปปิ้ง','พาราเบน',"ฝ้า"]
    words_list = set(thai_words())
    words_list.update(words)
    custom_dictionary_trie = Trie(words_list)
    return custom_dictionary_trie

