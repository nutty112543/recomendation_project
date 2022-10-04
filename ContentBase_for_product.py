import pandas as pd
import numpy as np
from nltk.corpus import stopwords
from sklearn.metrics.pairwise import linear_kernel
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize import RegexpTokenizer
from sklearn.metrics.pairwise import linear_kernel
import re
import string
import random
import requests
from io import BytesIO
import matplotlib.pyplot as plt
import pythainlp
from pythainlp import sent_tokenize, word_tokenize
from pythainlp.tokenize.multi_cut import find_all_segment, mmcut, segment
import MySQLdb

mydb = MySQLdb.connect(
      host="localhost",
      user="root",
      password="",
      database="skincare_project"
    )
mycursor = mydb.cursor()
mycursor.execute("Show tables;")
table = mycursor.fetchall()
    
print(table)



mycursor = mydb.cursor()
sql = "select product.product_id,product.img_list,product.product_name,brand.brand_name as 'brand',country.country_name as 'country',product.price AS price,skintype.skin_type_name as 'skin_type',product.detail,product.rating,product_type.product_type_name as 'product_type',product.detail2 from product join brand on product.brand_id = brand.brand_id JOIN country on product.country_id=country.country_id join skintype on product.skin_type_id = skintype.skin_type_id join product_type on product.product_type_id = product_type.product_type_id ORDER by product_id ASC;"
mycursor.execute(sql)
result = mycursor.fetchall()
df = pd.read_sql(sql, con=mydb)
df


from pythainlp.corpus import thai_stopwords
stopwords = list(thai_stopwords())
print(stopwords)




from pythainlp.tokenize import word_tokenize



text='Yanhee Mela Cream 20g ครีมลดฝ้า กระ จุดด่างดำ สูตรเฉพาะของยันฮี ผสานสารสกัดเข้มข้น แต่อ่อนโยนต่อผิว ช่วยฟื้นฟูผิวที่มีความหมองคล้ำ รอยฝ้า กระ จุดด่างดำ ทำให้ผิวหน้าแลดูเรียบเนียนกระจ่างใสขึ้น'
word_tokenize(text, engine="multi_cut")



from pythainlp.corpus.common import thai_words




from pythainlp.util import Trie



#สร้างคำใหม่ออกมากถ้าเจอคำเหล่านี้จะไม่ตัดแยกคำจะตัดรวมเป็นคำๆคำเดียวแบบนี้
words = ["ผิวมัน","ผิวแห้ง","ผิวผสม","ผิวปกติ","มอยซ์เจอไรเซอร์","เซรั่ม","เอสเซนส์","กันแดด","โลชั่น","โทนเนอร์","แอมพูล","มากส์","คลีนซิ่ง","ออยล์","อิมัลชั่น","ทรีทเมนท์",' ลิปบาล์ม','คลีนเซอร์','บิวตี้',"ออแกนิค",'ชีท','สลีปปิ้ง','พาราเบน',"ฝ้า"]
words_list = set(thai_words())
words_list.update(words)
custom_dictionary_trie = Trie(words_list)
newword=word_tokenize(text, custom_dict=custom_dictionary_trie)
print(newword)




for i in newword:
    if i not in stopwords:
        print(i)




def get_token_list(doc_text):
    tokens = word_tokenize(doc_text,custom_dict=custom_dictionary_trie) 
    return tokens




def remove_stopword(doct_text):
    stopword=[]
    for word in doct_text:
        if word not in stopwords:
              stopword.append(word)
    return stopword        




detail=df['detail'][0]
print(detail)
word =  get_token_list(detail)
print(word)
word2 = remove_stopword(word)
print(word2)




for i in range(0,len(df)):
    detail=df['detail'][i]
    detail2=df['detail2'][i]
    #print(detail)
    detail=get_token_list(detail)
    deatal = remove_stopword(detail)
    
    #print(detail)
    detail2=get_token_list(detail2)
    detail2 = remove_stopword(detail2)
    #print(detail2)
    Str2=" "
    for j in detail:
        Str2=Str2+j+" " 
    Str3=" "
    for j in detail2:
        Str3=Str3+j+" "    
    df['detail'][i] = Str2
    df['detail2'][i] = Str3
    print("detail1")
    print(Str2)
    print('detail2')
    print(Str3)
    print("----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
    print("\n")
    #print(df['detail'][i])



dta_list=[]
for i in range(len(df)):
    #print(df[i])
     x=df['brand'][i]+" "+df['country'][i]+" "+df['skin_type'][i]+" "+df['product_type'][i]+" "+str(df['price'][i])+" "+df['detail'][i]+" "+df['detail2'][i]
     print(x)
     dta_list.append(x)



for i in dta_list:
    print(i)



tf = TfidfVectorizer(analyzer='word')
tf_idf_matrix = tf.fit_transform(dta_list)
tfidf_array = np.array(tf_idf_matrix.todense())
data_tfidf = pd.DataFrame(tfidf_array,columns=tf.get_feature_names())
print(data_tfidf)
print(tf_idf_matrix)


from sklearn.metrics.pairwise import cosine_similarity
cosine_sim = cosine_similarity(tf_idf_matrix,tf_idf_matrix)
print(cosine_sim)



results = {} 
for idx, row in df.iterrows():
    #print(idx,row)
    similar_indices = cosine_sim[idx].argsort()[:-12:-1]
    similar_items = [(df['product_id'][i],df['product_name'][i],cosine_sim[idx][i]) for i in similar_indices]
    results[row['product_id']] = similar_items[1:]
results




c=0
answer = {}
for i in results:
    print("รหัสสินค้า: ",i,"",df['product_name'][c])
    print("สินค้าที่ใกล้เคียงคือ")
    c+=1
    sim_list = []
    for j in results[i]:
        if j[2]<=1:
            print("รหัสสินค้า :",j[0],"",j[1]," ค่า similarity คือ :",j[2])
            sim_list.append(j[0])
            answer[i] = sim_list
    print("-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")




df2=pd.DataFrame.from_dict(answer, orient='index',columns=['pd_sim_id_1', 'pd_sim_id_2','pd_sim_id_3', 'pd_sim_id_4', 'pd_sim_id_5','pd_sim_id_6','pd_sim_id_7','pd_sim_id_8','pd_sim_id_9','pd_sim_id_10'])
df2.to_csv('C:/Users/Administrator/Desktop/recom_code/similarity_product.csv')
df2







query = "ผิวแห้ง เป็นสิวอุดตัน รูขุมขนกว้าง"
query = get_token_list(query)
print(query)
query =  remove_stopword(query)
print(query)
q=' '.join(query)
print(q)
query_vector = tf.transform([q])
tfidf_array2= np.array(query_vector.todense())
print(query_vector)
data_tfidf2 = pd.DataFrame(tfidf_array2,columns=tf.get_feature_names())
data_tfidf2



cosine_sim2 = cosine_similarity(tf_idf_matrix,query_vector).flatten()
list(enumerate(cosine_sim2))




similar_indices2 = cosine_sim2.argsort()[:-11:-1]
print(similar_indices2)

for w in query:
    for i in similar_indices2:
        data=[df['product_id'][i],df['product_name'][i],df['skin_type'][i],df['detail2'][i],cosine_sim2[i]]
        print('รหัสสินค้า :',data[0]," ชื่อสินค้า :",data[1],"ค่า similarity :",data[4])
        print("ประเภทผิว: ",data[2])
        print("รายละเอียดสินค้า :",data[3])
        print("-----------------------------------------------------------------------------------------------------------------------------------------------")










