# @author shobhit bhadoria
import csv
import smtplib
from email.message import EmailMessage
from pathlib import Path
from string import Template
from flask import Flask,render_template,url_for,redirect,request
import re
import pickle
import lightgbm as lgb
f=open('finalized_model.sav', 'rb')


hn = []

app = Flask('app')

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/<string:page_name>')
def html_page(page_name):
    if page_name=="news.html":
        return data(hn,fields,filename)
    return render_template(page_name)

# app.run(host='0.0.0.0', port=8080)

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
def check(email):
    if(re.fullmatch(regex, email)):
        return True

    else:
        return False

def modell(n,p,k,t,h,ph,r):
        m =  pickle.load(f)
        p=m.predict([[n,p,k,t,h,ph,r]])
        f.close()
        return p[0]    

def write_to_database(data):
    with open('./database.txt',mode='a')as database:
        name=data["name"]
        email=data["email"]
        message=data['message']
        database.write(f'\n {name},{email},{message}')

def write_to_csv(data):
    with open('./database.csv',mode='a',newline='')as database2:
        name=data["name"]
        email=data["email"]
        message=data['message']
        csv_witer=csv.writer(database2,delimiter=',',quotechar='"',quoting=csv.QUOTE_MINIMAL)
        csv_witer.writerow([name,email,message])
def email_sender(data):
    name = data["name"]
    emailid = data["email"]
    html = Template(Path('./templates/email.html').read_text())
    email = EmailMessage()
    email['from'] = 'shobhit bhadoria'
    email['to'] = emailid
    email['subject'] = 'Your Feedback submitted!'

    email.set_content(html.substitute({'name': name}), 'html')

    with smtplib.SMTP(host='smtp.gmail.com', port=587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login('gmail', 'password')
        smtp.send_message(email)


def form_reminder(data):
    name = data["name"]
    emailid = data["email"]
    message = data['message']
    email = EmailMessage()
    email['from'] = 'shobhit bhadoria'
    email['to'] = 'shobhitbhadoriya123@gmail.com'
    email['subject'] = 'Feedback received!'

    email.set_content(f'Form received:\n sender name: {name}\n sender id: {emailid}\nmessage: {message}')

    with smtplib.SMTP(host='smtp.gmail.com', port=587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login('gmail', 'password')
        smtp.send_message(email)

def pred_mail(data):
    form_reminder(data)
    if data["name"]=='':
        return 0
    name = data["name"]
    emailid = data["email"]
    message = data['message']
    email = EmailMessage()
    email['from'] = 'shobhit bhadoria'
    email['to'] = emailid
    email['subject'] = 'Your prediction details!'
    email.set_content(f'Form received:\n sender name: {name}\n sender id: {emailid}\nmessage: {message}')

    with smtplib.SMTP(host='smtp.gmail.com', port=587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login('gmail', 'password')
        smtp.send_message(email)

@app.route('/submit_form',methods=['POST','GET'])
def Sumbit_form():
    if request.method=='POST':
        try:
            data=request.form.to_dict()
            if check(data["email"])==0:
                return 'Incorrect Email try again'
            write_to_csv(data)
            write_to_database(data)
            email_sender(data)
            form_reminder(data)
            return redirect('/thankyou.html')
        except:
            return 'didnt save to database'
    else:
        return 'woops,Something went wrong'

@app.route('/crop_form',methods=['POST','GET'])
def crop_form():
    if request.method=='POST':
        try:
            cdata=request.form.to_dict()

            N = float(cdata['n'])
            P = float(cdata['p'])
            K = float(cdata['k'])
            temperature = float(cdata['t'])
            humidity = float(cdata['h'])
            pH = float(cdata['ph'])
            rainfall = float(cdata['r'])
            crop_name =modell(N,P,K,temperature ,humidity,pH,rainfall)
            cdata["message"] = f' N={N}, P={P}, k={K}, temperature={temperature}, humidity={humidity}, ph= {pH}, rainfall= {rainfall} , Crop name : {crop_name}'
            write_to_csv(cdata)
            write_to_database(cdata)
            pred_mail(cdata)
            return render_template('generic.html',crop_name=crop_name,n=float(cdata['n']),p=float(cdata['p']),k=float(cdata['k']),t=float(cdata['t']),h=float(cdata['h']),ph=float(cdata['ph']),r=float(cdata['r']))
        except:
            return 'Didnt save to database,Try again'
    else:
        return 'woops,Something went wrong, Try again'








# go to webserver path
# py -3 -m venv venv
# venv\Scripts\activate
# python3 -m pip install Flask
# set FLASK_APP=server.py
# $env:FLASK_APP = "server.py"
# $env:FLASK_ENV = "development"
# python3 -m flask run
