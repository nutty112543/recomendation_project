import word_manage
from email.policy import default
import math
from flask import Flask, render_template, request, redirect, url_for, session,flash,jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from flask_paginate import Pagination, get_page_args 
import sys
import logging
import re
import bcrypt
from flask_mail import Mail,Message
from random import randint
import pythainlp

#from pythainlp.corpus import thai_stopwords
#from pythainlp.tokenize import word_tokenize
#from pythainlp.corpus.common import thai_words
#from pythainlp.util import Trie
import pandas as pd
import numpy as np

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)
#เชื่อต่อดาต้าเบสที่ใช้งาน
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'skincare_project'
mysql = MySQL(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'sirijunyapong_n2@silpakorn.edu'
app.config['MAIL_PASSWORD'] = 'Nutty52594'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
#------------------------------------------------------------------------------------------ส่วนเรียกใช้ model--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Dataframe ของสินค้า
mydb = MySQLdb.connect(
      host="localhost",
      user="root",
      password="",
      database="skincare_project"
    )

mycursor = mydb.cursor()
sql = "select product.product_id,product.img_list,product.product_name,brand.brand_name as 'brand',country.country_name as 'country',product.price AS price,skintype.skin_type_name as 'skin_type',product.detail,product.rating,product_type.product_type_name as 'product_type',product.detail2 from product join brand on product.brand_id = brand.brand_id JOIN country on product.country_id=country.country_id join skintype on product.skin_type_id = skintype.skin_type_id join product_type on product.product_type_id = product_type.product_type_id ORDER by product_id ASC;"
mycursor.execute(sql)
result = mycursor.fetchall()
df = pd.read_sql(sql, con=mydb)
#print(df)

#เพิ่มคำศัพท์ใหม่ที่เราต้องการลงไปในThai dict
#def new_word_dict():
    #words = ["ผิวมัน","ผิวแห้ง","ผิวผสม","ผิวปกติ","มอยซ์เจอไรเซอร์","เซรั่ม","เอสเซนส์","กันแดด","โลชั่น","โทนเนอร์","แอมพูล","มากส์","คลีนซิ่ง","ออยล์","อิมัลชั่น","ทรีทเมนท์",' ลิปบาล์ม','คลีนเซอร์','บิวตี้',"ออแกนิค",'ชีท','สลีปปิ้ง','พาราเบน',"ฝ้า"]
    #words_list = set(thai_words())
    #words_list.update(words)
    #custom_dictionary_trie = Trie(words_list)
    #return custom_dictionary_trie

#stopword ตัดคำที่เป็นstopword ออก
#def remove_stopword(doct_text):
    #stopwords = list(thai_stopwords())
    #print(stopwords)
    #stopword=[]
    #for word in doct_text:
        #if word not in stopwords:
              #stopword.append(word)
    #return stopword 

#ตัดคำของtextนั้น
#def get_token_list(doc_text):
    #tokens = word_tokenize(doc_text,custom_dict=new_word_dict()) 
    #return tokens
#---------------------------------------------------------------------------------------------Login Register------------------------------------------------
@app.route('/new_password/user/<email>',methods=["GET","POST"])
def new_password(email):
    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            flash("โปรดกรอกรหัสผ่านให้เหมือนกัน","error")
           
        elif len(password)<6:
            flash("โปรดกรอกรหัสผ่านมากกว่า 6 ตัวอักษร","error")
         
        elif re.search(r'[A-Z]', password) == None and re.search(r'[a-z]', password)==None:
            flash("ควรมีตัวอักษร พิมพ์เล็กและพิมพ์ใหญ่ ในรหัสผ่าน อย่างน้อย 1 ตัวอักษร","error")
           
        elif re.search(r'[A-Z]', password) == None:
            flash("ควรมีตัวอักษร พิมพ์ใหญ่ ในรหัสผ่าน อย่างน้อย 1 ตัวอักษร","error")
            
        elif re.search(r'[a-z]', password) == None:
            flash("ควรมีตัวอักษร พิมพ์เล็ก ในรหัสผ่าน อย่างน้อย 1 ตัวอักษร","error")
           
        else:
            my_cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  
            change_password = "update user set password='{}',confirm_password='{}' where email='{}'".format(password,confirm_password,email)
            my_cur.execute(change_password)
            my_cur.connection.commit()
            print(change_password)
            flash("เปลี่ยนรหัสผ่านสำเร็จ","success")
            return redirect(url_for("login"))
    return render_template('new_password.html')

@app.route('/verify_forget_pw/user/<email>',methods=["GET","POST"]) 
def verify_forget_pw(email):
    if request.method == 'POST':
        otp_number = request.form['otp_number']
        otp_number2 = request.form['otp_number2']
        otp_number3 = request.form['otp_number3']
        otp_number4 = request.form['otp_number4']
        otp_number5 = request.form['otp_number5']
        otp_number6 = request.form['otp_number6']
        otp=otp_number+otp_number2+otp_number3+otp_number4+otp_number5+otp_number6
        otp_forget=session['forget_pw_otp']
        if(otp==otp_forget):
            flash("ยืนยันตัวตนสำเร็จ","success")
            my_cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            update_status="update user set otp={} where email='{}'".format(int(otp),email)
            my_cur.execute(update_status)
            my_cur.connection.commit()
            print(email)
            return redirect(url_for("new_password",email=email))
        else:
           flash("หมายเลข OTP ไม่ถูกต้อง โปรดตรวจสอบ","error") 
    return render_template("verify_forget_pw.html")

@app.route('/forget_password',methods=["GET","POST"])   
def forget_password():
    if request.method == 'POST':
        email = request.form['email']
        my_cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = "select * from user where email ='{}'".format(email)
        my_cur.execute(sql)
        result = my_cur.fetchall()
        if (result):
            for r in result:
                print(r['email'])
                if email == r['email']:
                    flash("Email Address ถูกต้อง","success")
                                    
                    #ส่งเลขOTP ไปหาemailจริงๆ
                    otp=randint(000000,999999)
                    msg=Message(subject='หมายเลข OTP ในการเปลี่ยนรหัสผ่านของท่าน',sender='sirijunyapong_n2@silpakorn.edu',recipients=[email])
                    msg.body="หมายเลข OTP ในการยืนยันตัวตนของท่าน :"+str(otp)
                    session['forget_pw_otp']=str(otp)
                    print(session['forget_pw_otp'])
                    mail.send(msg)
                    session['email']=email
                    return  redirect(url_for('verify_forget_pw',email = email))
                 
        else:   
            flash("Email Address ไม่ถูกต้องกรุณาตรวจสอบ Email Address ของท่าน","error")
    return render_template('forget_password.html')

@app.route('/verify_email/user_id/<int:id>',methods=["GET","POST"])
def verify_email(id):
    flash("ลงทะเบียนสำเร็จ กรุณายืนยันตัวตนผ่าน Email","success")
    if request.method == 'POST':
        otp_number = request.form['otp_number']
        otp_number2 = request.form['otp_number2']
        otp_number3 = request.form['otp_number3']
        otp_number4 = request.form['otp_number4']
        otp_number5 = request.form['otp_number5']
        otp_number6 = request.form['otp_number6']
        #print(otp_number,otp_number2,otp_number3,otp_number4,otp_number5,otp_number6)
        otp=otp_number+otp_number2+otp_number3+otp_number4+otp_number5+otp_number6
        #print(otp,"",type(otp))
        otp_user=session['otp_user']
        if(otp==otp_user):
            flash("ยืนยันตัวตนสำเร็จ","success")
            my_cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            update_status="update user set otp={},verify_email='Yes' where user_id={}".format(int(otp),id)
            my_cur.execute(update_status)
            my_cur.connection.commit()
            return redirect(url_for('login'))
        else:
            flash("หมายเลข OTP ไม่ถูกต้อง โปรดตรวจสอบ","error")
    return render_template('verify_email.html')
    

@app.route('/',methods=["GET","POST"])
def login():   
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        my_cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = "select * from user where email='{}'".format(email)
        my_cur.execute(sql)
        result = my_cur.fetchall()
        if result:
            for r in result:
                print(r)
                if email==r['email'] and password==r['password']: 
                    if(r['verify_email']=="Yes"):
                        session['username']=r['first_name']
                        return redirect(url_for('product'))
                    else:
                        flash("คุณยังไม่ได้ทำการยืนยันตัวตน","error")
                else:
                    flash("Email หรือ Password ไม่ถูกต้อง กรุณาตรวจสอบ","error")
        else:
            flash("ท่านยังไม่ได้ทำการสมัครสมาชิก","error")
    return render_template('login.html')


@app.route('/register',methods=["GET","POST"])
def register():

    if request.method == 'POST' and 'first_name' in request.form and 'last_name' in request.form and 'email' in request.form and 'password' in request.form and 'confirm_password' in request.form and 'gender' in request.form and 'age' in request.form and 'skin_type' in request.form and 'problem_skin' in request.form and 'other_problem' in request.form:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        gender= request.form['gender']
        age = request.form['age']
        skin_type = request.form['skin_type']
        problem_skin = request.form.getlist("problem_skin")
        other_problem = request.form['other_problem']
        otp=randint(000000,999999)

        if password != confirm_password:
            flash("โปรดกรอกรหัสผ่านให้เหมือนกัน","error")
           
        elif len(password)<6:
            flash("โปรดกรอกรหัสผ่านมากกว่า 6 ตัวอักษร","error")
         
        elif re.search(r'[A-Z]', password) == None and re.search(r'[a-z]', password)==None:
            flash("ควรมีตัวอักษร พิมพ์เล็กและพิมพ์ใหญ่ ในรหัสผ่าน อย่างน้อย 1 ตัวอักษร","error")
           
        elif re.search(r'[A-Z]', password) == None:
            flash("ควรมีตัวอักษร พิมพ์ใหญ่ ในรหัสผ่าน อย่างน้อย 1 ตัวอักษร","error")
            
        elif re.search(r'[a-z]', password) == None:
            flash("ควรมีตัวอักษร พิมพ์เล็ก ในรหัสผ่าน อย่างน้อย 1 ตัวอักษร","error")
           
        else:
            
            #hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            #hashed_password2 = bcrypt.hashpw(confirm_password.encode('utf-8'), bcrypt.gensalt())
            problem_skin =','.join(problem_skin)
            #print(problem_skin)
           # print(hashed_password,hashed_password2)
            my_cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  
            user_check = "select * from user where email ='{}' limit 1".format(email)
            my_cur.execute(user_check)
            result = my_cur.fetchall()
             
            if(result):
                #checkemail
                for r in result:
                    #print(r['email'])
                    
                    if r['email']==email:
                        flash("email นี้มีคนใช้ไปแล้ว","error")
                    
            else:
                user_check = "insert into user(first_name,last_name,email,password,confirm_password,gender,age,skin_type,problem_skin,other_problem) values ('{}','{}','{}','{}','{}','{}',{},'{}','{}','{}')"\
                    .format(first_name,last_name,email,password,confirm_password,gender,age,skin_type,problem_skin,other_problem)
           
                #print(user_check)
                my_cur.execute(user_check)
                my_cur.connection.commit()
                
                
                #ส่งเลขOTP ไปหาemailจริงๆ
                msg=Message(subject='หมายเลข OTP ของท่าน',sender='sirijunyapong_n2@silpakorn.edu',recipients=[email])
                msg.body="หมายเลข OTP ในการยืนยันตัวตนของท่าน :"+str(otp)
                session['otp_user']=str(otp)
                mail.send(msg)
                
                my_cur.close() 
                my_cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
                sql = "select user_id from user where email='{}'".format(email)
                my_cur.execute(sql)
                result2=my_cur.fetchall()
                #print(result2)
                for r in result2:
                   id = r['user_id']
                   #print(id)
                   session['id']=id
                my_cur.close() 
                return  redirect(url_for('verify_email',id = id))
               
    return render_template('register.html')
#---------------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/home')
def home():
    #print(country)
    return render_template('home.html')

@app.route('/user/product',methods=["GET","POST"])
def product():
    #query brand
    my_cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql = "select DISTINCT brand.brand_name as 'brand',count(*) as 'count' from product join brand on product.brand_id = brand.brand_id JOIN country on product.country_id=country.country_id join skintype on product.skin_type_id = skintype.skin_type_id join product_type on product.product_type_id = product_type.product_type_id GROUP by product.brand_id HAVING COUNT(*) > 1;"
    my_cur.execute(sql)
    brand = my_cur.fetchall()
    #print(brand)
    
    #query country
    sql = "select DISTINCT country.country_name as 'country',count(*) as 'count' from product join brand on product.brand_id = brand.brand_id JOIN country on product.country_id=country.country_id join skintype on product.skin_type_id = skintype.skin_type_id join product_type on product.product_type_id = product_type.product_type_id GROUP by product.country_id HAVING COUNT(*) > 1;"
    my_cur.execute(sql)
    country = my_cur.fetchall()
    #print(country)
    
    #query skin_type
    sql = "select DISTINCT skintype.skin_type_name as 'skin_type',count(*) as 'count' from product join brand on product.brand_id = brand.brand_id JOIN country on product.country_id=country.country_id join skintype on product.skin_type_id = skintype.skin_type_id join product_type on product.product_type_id = product_type.product_type_id GROUP by product.skin_type_id HAVING COUNT(*) > 1;"
    my_cur.execute(sql)
    skin_type = my_cur.fetchall()
    #print(skin_type)

    #query product_type
    sql = "select DISTINCT product_type.product_type_name as 'product_type',count(*) as 'count' from product join brand on product.brand_id = brand.brand_id JOIN country on product.country_id=country.country_id join skintype on product.skin_type_id = skintype.skin_type_id join product_type on product.product_type_id = product_type.product_type_id GROUP by product.product_type_id HAVING COUNT(*) > 1;"
    my_cur.execute(sql)
    product_type = my_cur.fetchall()
    #print(product_type)
    
    if request.method =='POST':
        brand_search = request.form['brand_search']
        #product_type_search = request.form['product_type_search']
        if brand_search==" ":
            my_cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            sql = "select DISTINCT brand.brand_name as 'brand',count(*) as 'count' from product join brand on product.brand_id = brand.brand_id JOIN country on product.country_id=country.country_id join skintype on product.skin_type_id = skintype.skin_type_id join product_type on product.product_type_id = product_type.product_type_id GROUP by product.brand_id HAVING COUNT(*) > 1;"
            my_cur.execute(sql)
            brand = my_cur.fetchall()
        else:
            sql="select DISTINCT brand.brand_name as 'brand',count(*) as 'count' from product join brand on product.brand_id = brand.brand_id JOIN country on product.country_id=country.country_id join skintype on product.skin_type_id = skintype.skin_type_id join product_type on product.product_type_id = product_type.product_type_id WHERE brand.brand_name like '{}%' GROUP by product.brand_id HAVING COUNT(*) > 1".format(brand_search)
            print(sql)
            my_cur.execute(sql)
            brand = my_cur.fetchall()


    flash("เข้าสู่ระบบสำเร็จ","success")
    return render_template('product.html',brand=brand,country=country,skin_type=skin_type,product_type=product_type)
                           
                           
@app.route('/response_product',methods=["GET","POST"])
def response_product():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        query = request.form['action']
        brand = request.form.getlist('brand[]')
        country = request.form.getlist('country[]')
        skin_type=request.form.getlist('skin_type[]')
        product_type=request.form.getlist('product_type[]')
        page_num = request.form.get('page',1)
        min_price = request.form['min_price']
        max_price = request.form['max_price']
        print("form", request.form)
        print(min_price," ",max_price)
        #print(query)
        #print(brand)
        brand2 = "','".join(brand)
        country2="','".join(country)
        skin_type2="','".join(skin_type)
        product_type2="','".join(product_type)
        #print(brand2)
        #print(country2)
        sql = "select product.product_id,product.img_list,product.product_name,brand.brand_name as 'brand',country.country_name as 'country',product.price,skintype.skin_type_name as 'skin_type',product.detail,product.rating,product_type.product_type_name as 'product_type',product.detail2 from product join brand on product.brand_id = brand.brand_id JOIN country on product.country_id=country.country_id join skintype on product.skin_type_id = skintype.skin_type_id join product_type on product.product_type_id = product_type.product_type_id where product_status=1"
        #print(sql)
        cur.execute(sql)
        #productlist = cur.fetchall() 
       
        page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')
        #print(page)
        #print(per_page)
        #print(offset)
        total = cur.rowcount
        per_page=32
        sql2 = "select product.product_id,product.img_list,product.product_name,brand.brand_name as 'brand',country.country_name as 'country',product.price,skintype.skin_type_name as 'skin_type',product.detail,product.rating,product_type.product_type_name as 'product_type',product.detail2 from product join brand on product.brand_id = brand.brand_id JOIN country on product.country_id=country.country_id join skintype on product.skin_type_id = skintype.skin_type_id join product_type on product.product_type_id = product_type.product_type_id ORDER by product_id LIMIT {} OFFSET {}" \
        .format(per_page, offset)  
      
        #print(sql2)
        cur.execute(sql2)
        productlist = cur.fetchall() 
   
        pagination = Pagination(page=int(page_num),
                            per_page=per_page,
                            total=total,href='javascript:change_page({0})',
                            css_framework='bootstrap4')
                           
        print('all list')
        if brand or country or skin_type or product_type or min_price or max_price:
            if brand:
                sql=sql+" and brand.brand_name in ('{}')".format(brand2)
                #print(sql)
                cur.execute(sql)
                productlist = cur.fetchall()
                #print(productlist)
            if country:
                sql = sql+" and country.country_name in ('{}')".format(country2)
                #print(sql)
                cur.execute(sql)
                productlist = cur.fetchall()
            if skin_type:
                sql = sql+" and skintype.skin_type_name in ('{}')".format(skin_type2)
                #print(sql)
                cur.execute(sql)
                productlist = cur.fetchall()
            if product_type:
                sql = sql+" and product_type.product_type_name in ('{}')".format(product_type2)
                #print(sql)
                cur.execute(sql)
                productlist = cur.fetchall()
            if min_price or max_price: 
                sql = sql+" and product.price  BETWEEN {} AND {}".format(min_price,max_price)
                print(sql)
                cur.execute(sql)
                productlist = cur.fetchall()
                
            sql=sql+" ORDER by product_id LIMIT {} OFFSET {}" .format(per_page, offset)
            #print(sql)
            total = cur.rowcount
            pagination = Pagination(page=int(page_num),
                        per_page=per_page,
                        total=total,href='javascript:change_page({0})',
                        css_framework='bootstrap4')
            cur.execute(sql)
            productlist = cur.fetchall()         
    return  render_template('response_product.html', record_name='productlist',page=page,per_page=per_page,pagination=pagination,productlist=productlist,brand=brand)


@app.route('/product/<int:id>')
def detail_product(id):
       app.logger.info('Processing default request')
       my_cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
       sql = "select product.product_id,product.img_list,product.product_name,brand.brand_name as 'brand',country.country_name as 'country',product.price,skintype.skin_type_name as 'skin_type',product.detail,product.rating,product_type.product_type_name as 'product_type',product.detail2 from product join brand on product.brand_id = brand.brand_id JOIN country on product.country_id=country.country_id join skintype on product.skin_type_id = skintype.skin_type_id join product_type on product.product_type_id = product_type.product_type_id where product.product_id={}".format(id)
       my_cur.execute(sql)
       result = my_cur.fetchall()
       sql2 = "select pd_sim_id_1,pd_sim_id_2,pd_sim_id_3,pd_sim_id_4,pd_sim_id_5,pd_sim_id_6,pd_sim_id_7,pd_sim_id_8,pd_sim_id_9,pd_sim_id_10 from similarity_product where product_id={}".format(id)
       my_cur.execute(sql2)
       result2 = my_cur.fetchall()
       list1=[]
       #print(result2)
       for i in result2:
        for j in i:
            #print(i[j])
            sql3 ="select product.product_id,product.img_list,product.product_name,brand.brand_name as 'brand',country.country_name as 'country',product.price,skintype.skin_type_name as 'skin_type',product.detail,product.rating,product_type.product_type_name as 'product_type' from product join brand on product.brand_id = brand.brand_id JOIN country on product.country_id=country.country_id join skintype on product.skin_type_id = skintype.skin_type_id join product_type on product.product_type_id = product_type.product_type_id where product.product_id in ("+str(i[j])+") order by product.product_id;"
            my_cur.execute(sql3)
            result3= my_cur.fetchall()
            #print(result3)
            #rint(sql3)
            list1.append(result3)
       return render_template('product_detail.html',result1=result,result3=list1) 
       

if __name__ == '__main__':
    app.secret_key = '1234'
    app.run(debug=True)