print("Started Program")
print("Initiating Modules")

import matplotlib.pyplot as plt
import datetime as dt,re
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
nlp = spacy.load("en_core_web_sm")
from wordcloud import WordCloud
import numpy as np
import pandas as pd
import mysql.connector as con
from textblob import TextBlob
from sklearn import svm
from sklearn.model_selection import train_test_split
import pandas as pd
from sklearn.metrics import accuracy_score
import datetime as dt

class BasicUtils(): #Basic Utils

    def __init__(self):
        print("Modules Initiated")
        self.DBInstanc = con.connect(user = 'root',password = 'shaam2023',host = 'localhost')
        self.ICUR = self.DBInstanc.cursor()
        print("Primary MYSQL Instance Initiated")

    def fetchtime(self):
        time=dt.datetime.now().time().strftime('%I:%M:%S %p')
        return time
    
    def welmsg(self,name):
        self.name=name
        if dt.datetime.now().hour<12:
            return f"Good Morning {self.name}"
        elif dt.datetime.now().hour>= 12 and dt.datetime.now().hour<16:
            return f"Good Afternoon {self.name}"
        elif dt.datetime.now().hour>= 16 and dt.datetime.now().hour<19:
            return f"Good Evening {self.name}"
        elif dt.datetime.now().hour>= 19 and dt.datetime.now().hour<23:
            return f"Good Night {self.name}"
        else:
            return f"Sweet Dreams {self.name}"
        
    def getdate(self):
        self.d,self.m,self.y = dt.datetime.now().day,dt.datetime.now().month,dt.datetime.now().year
        return f'{self.d}-{self.m}-{self.y}'
    
    def today(self):
        return dt.date.today().strftime("%A")
    
    def readfromxlsx(self):
        self.data = pd.read_excel('./Subfiles/Sentiment Analysis.xlsx')

    def preprocess(self,text):
        self.text = text
        self.Stop = set(STOP_WORDS)
        self.Stage1 = re.compile("["u"\U0001F600-\U0001F64F"u"\U0001F300-\U0001F5FF"u"\U0001F680-\U0001F6FF"u"\U0001F1E0-\U0001F1FF"u"\U00002702-\U000027B0"u"\U000024C2-\U0001F251""]+", flags = re.UNICODE)
        self.Result1 = self.Stage1.sub(r'',self.text)
        self.outputxt = ''
        self.elements = nlp(self.Result1)

        Y = [token for token in self.elements]

        for token in Y:
            if str(token.text).isalpha()!=True:
                Y.remove(token)
                continue
            self.outputxt += str(token.lemma_)+' '

        return self.outputxt
    
    def write(self):
        for i in range(self.data.shape[0]):
            self.ICUR.execute(f"insert into sap values ({TextBlob(str(self.data['reviewtext'][i])).sentiment.subjectivity},{TextBlob(str(self.data['reviewtext'][i])).sentiment.polarity},NULL)")
            self.DBInstanc.commit()
            print(f"W IN PROGRESS: {300*i/self.data.shape[0]}",end='\r')

    def modelTrain(self):
        # init var
        self.data = pd.read_sql('select * from sap.sap',self.DBInstanc)
        self.X,self.y = self.data.iloc[:, :-1], self.data.iloc[:, [-1]]
        self.model = svm.SVC(kernel='poly')
        self.X_train,self.X_test,self.y_train,self.y_test=train_test_split(self.X,self.y,test_size=0.2)
        self.model.fit(self.X_train,self.y_train)
        self.prediction = self.model.predict(self.X_test)
        print(accuracy_score(self.y_test,self.prediction)*100,"%")

    def Sentiment(self,text):
        Y = BasicUtils()
        self.text=text
        self.features = pd.DataFrame(columns=['Subjectivity','Polarity'],data=[[TextBlob(Y.preprocess(self.text)).sentiment.subjectivity,TextBlob(Y.preprocess(self.text)).sentiment.polarity]])
        self.y = self.model.predict(self.features)

        if self.y == [-1.]:
            print("Negative")
            return (-1)
        elif self.y == [1.]:
            print("Positive")
            return (1)
        elif self.y == [0.]:
            print("Neutral")
            return (0)
        
Y = BasicUtils()
Y.modelTrain()