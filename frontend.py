import os,csv,pickle,datetime as dt,flet as ft,time
from matplotlib import rcParams
import mysql.connector as con,matplotlib.pyplot as plt,numpy as np
from wordcloud import WordCloud
from spacy.lang.en.stop_words import STOP_WORDS
from backend import BasicUtils
from mysql.connector import errors
Backend=BasicUtils()
ICUR=Backend.ICUR
DBInstanc=Backend.DBInstanc
# Backend=BasicUtils()
# ICUR=Backend.ICUR
user_is_admin=False
def BarPlot(rx,path,Title):
    X = list(rx.keys())
    y = list(rx.values())
    rcParams['font.size']=20 
    plt.figure(figsize = (8, 8))
    plt.bar(X, y, color ='blue',width = 0.4)
    plt.xlabel("Star Rating")
    plt.ylabel("No. of Customers")
    plt.title=Title
    os.system(f'if exist {path} del {path}')
    plt.savefig(path)
def SentimentPlot(data:dict,path,Title):
    Sentiment=list(data.keys())
    rcParams['font.size']=20
    Count = np.array(list(data.values()))
    fig=plt.figure(figsize=(8,8))
    plt.pie(Count,labels=Sentiment,colors=['green','yellow','red']) #+0- ORDER
    plt.title=Title
    os.system(f'if exist {path} del {path}')
    plt.savefig(path)
    print("Image Saved to Subfiles")
def Wordcloud(src,path,Title):
    src=src
    comment_words = ''
    stopwords = set(STOP_WORDS)
    for comments in src:
        comments=BasicUtils().preprocess(comments)
        tokens=comments.split()
        for i in range(len(tokens)):
            tokens[i]=tokens[i].lower()
        comment_words += " ".join(tokens)+" "
    PLOT = WordCloud(width = 800, height = 800,background_color ='white',stopwords =stopwords,min_font_size = 10).generate(comment_words)
    plt.figure(figsize = (8, 8), facecolor = None)
    plt.title=Title
    plt.axis("off")
    plt.imshow(PLOT)
    plt.tight_layout(pad = 0)
    os.system(f'if exist {path} del {path}')
    plt.savefig(path)
def AdminUI(page:ft.Page):
    color60= """#040D12""" #ui
    color30= """#F3FDE8""" #text
    color10= """#337CCF""" #buttons
    page.window_full_screen=True
    page.theme_mode=ft.ThemeMode.DARK
    page.title="Sentiment Analysis App"
    global fetchProdFeedbacksfromDB,fetchRatingsfromDB,fetchProductpreferencesfromDb,fetchServiceFeedbacksfromDB,SentimentScore
    def connectionrefresh():
        global DBInstanc,ICUR
        DBInstanc.close()
        DBInstanc = con.connect(user = 'root',password = 'shaam2023',host = 'localhost',database=f'{Base}')
        ICUR = DBInstanc.cursor()
    def survey_isrunn():
        found=False
        ICUR.execute(f'use {Base}')
        ICUR.execute('show tables')
        for j in ICUR.fetchall():
            if 'opensurvey' in j[0]:
                found = True
                break
            elif 'closedsurvey' in j[0]:
                found= False
            else:
                found=False
        page.update()
        return found
    X=ItemMapSql()
    def getSID():
        ICUR.execute('select * from surveytablelog where openonrt=1')
        co1=ICUR.fetchall()
        cn = bool(len(co1)!=0)
        match cn:
            case True:
                ICUR.execute(f'select survid from {Base}.surveytablelog where openonrt=1')
                SuID=ICUR.fetchall()[0][0]
            case False:
                SuID=int(SID.value)
        return SuID
    page.bgcolor=color60
    def fetchRatingsfromDB(stb='opensurvey'):
        Y={}
        for i in range(1,6):
            ICUR.execute(f'select count(*) from {stb} where srvratn={i}')
            Y[i]=ICUR.fetchall()[0][0]
        return Y
    def fetchProdFeedbacksfromDB(stb='opensurvey'):
        Y=[]
        match stb:
            case 'opensurvey':
                ICUR.execute(f'select PRODFED from {stb}')
                op=ICUR.fetchall()
            case _:
                ICUR.execute(f'select PRODFED from {stb}')
                op=ICUR.fetchall()               
        for i in range(len(op)):
            Y.append(op[i][0])
        return Y
    def fetchServiceFeedbacksfromDB(stb='opensurvey'):
        Y=[]
        match stb:
            case 'opensurvey':
                ICUR.execute(f'select servfdb from opensurvey')
                op=ICUR.fetchall()
            case _:
                ICUR.execute(f'select servfdb from {stb}')
                op=ICUR.fetchall()
        for i in range(len(op)):
            Y.append(op[i][0])
        return Y
    def SentimentScore(X0:list):
        Y={"Positive":0,"Neutral":0,"Negative":0}
        System=BasicUtils()
        System.modelTrain()
        for st in X0:
            Score=System.Sentiment(st)
            match Score:
                case 1:
                    Y["Positive"]+=1
                case 0:
                    Y["Neutral"]+=1
                case -1:
                    Y["Negative"]+=1
        return Y
    def fetchProductpreferencesfromDb(stb='opensurvey',sid=None):
        match stb:
            case 'opensurvey':
                Y={}
                Records=[]
                ICUR.execute('select ProductType from surveytablelog where openonrt=1')
                PT=ICUR.fetchall()[0][0]
                ICUR.execute(f'select Itemname from stocktable where Itemtype="{PT}"')
                o=ICUR.fetchall()
                for i in range(len(o)):
                    Y[o[i][0]]=0
                ICUR.execute(f'select PRODPREF from opensurvey')
                op=ICUR.fetchall()
                for i in range(len(op)):
                    op[i]=op[i][0]
                    for j in list(Y.keys()):
                        if op[i]==j:
                            Y[op[i]]+=1
                for el in Y:
                    Record=ft.DataRow()
                    Record.cells.append(ft.DataCell(ft.Text(el,color=color30,size=35)))
                    Record.cells.append(ft.DataCell(ft.Text(str(Y[el]),color=color30,size=35)))
                    Records.append(Record)
                return Records
            case _:
                Y={}
                Records=[]
                ICUR.execute(f'select ProductType from surveytablelog where survid={sid}')
                PT=ICUR.fetchall()[0][0]
                ICUR.execute(f'select Itemname from stocktable where Itemtype="{PT}"')
                o=ICUR.fetchall()
                for i in range(len(o)):
                    Y[o[i][0]]=0
                ICUR.execute(f'select PRODPREF from {stb}')
                op=ICUR.fetchall()
                for i in range(len(op)):
                    op[i]=op[i][0]
                    for j in list(Y.keys()):
                        if op[i]==j:
                            Y[op[i]]+=1
                return Y
    def count():
        ICUR.execute('select count(*) from opensurvey')
        c=ICUR.fetchall()[0][0]
        return c
    def e1(e):
        connectionrefresh()
        page.floating_action_button=ft.FloatingActionButton(width=90,content=ft.Row([ft.Icon(ft.icons.NIGHTLIFE,color=color30),ft.Text("Relax",color=color30)]),bgcolor=ft.colors.TRANSPARENT,on_click=sleep)
        match survey_isrunn():
            case True:
                global PTYP,PRFD
                ICUR.execute(f"select producttype from surveytablelog where Survid={getSID()}")
                PTYP=ICUR.fetchall()[0][0]
                ICUR.execute(f"select productname from surveytablelog where Survid={getSID()}")
                PRFD=ICUR.fetchall()[0][0]
                Ratings=fetchRatingsfromDB()
                PrSent=SentimentScore(fetchProdFeedbacksfromDB())
                SrSent=SentimentScore(fetchServiceFeedbacksfromDB())
            case False:
                Ratings={1:0,2:0,3:0,4:0,5:0}
                PRFD=None
                PTYP=None
                PrSent={"Positive":0,"Negative":0,"Neutral":0}
                SrSent={"Positive":0,"Negative":0,"Neutral":0}
        RATINGB=ft.Container(width=1000,
        content=ft.Row(alignment=ft.MainAxisAlignment.CENTER,controls=[
            ft.PieChart(
                sections=[
                    ft.PieChartSection(
                        Ratings[1],
                        color=ft.colors.BLUE,
                        radius=90,
                        border_side=ft.BorderSide(0, ft.colors.with_opacity(0, ft.colors.WHITE)),
                        title="1",
                        title_style=ft.TextStyle(color=color30)
                    ),
                    ft.PieChartSection(
                        Ratings[2],
                        color=ft.colors.RED,
                        radius=90,
                        border_side=ft.BorderSide(0, ft.colors.with_opacity(0, ft.colors.WHITE)),
                        title="2",
                        title_style=ft.TextStyle(color=color30)
                    ),
                    ft.PieChartSection(
                        Ratings[3],
                        color=ft.colors.PINK,
                        radius=90,
                        border_side=ft.BorderSide(0, ft.colors.with_opacity(0, ft.colors.WHITE)),
                        title="3",
                        title_style=ft.TextStyle(color=color30)
                    ),
                    ft.PieChartSection(
                        Ratings[4],
                        color=ft.colors.GREEN,
                        radius=90,
                        border_side=ft.BorderSide(0, ft.colors.with_opacity(0, ft.colors.WHITE)),
                        title="4",
                        title_style=ft.TextStyle(color=color30)
                    ),
                    ft.PieChartSection(
                        Ratings[5],
                        color=ft.colors.AMBER,
                        radius=90,
                        border_side=ft.BorderSide(0, ft.colors.with_opacity(0, ft.colors.WHITE)),
                        title="5",
                        title_style=ft.TextStyle(color=color30)
                    ),
                ],
        sections_space=1,
        center_space_radius=0,
        expand=True,
    ),ft.Text(color=color30,value=f"Service Rating",size=40)]))
        SRVFDBK=ft.Container(width=1000,
        content=ft.Row(alignment=ft.MainAxisAlignment.CENTER,controls=[ft.PieChart(
        sections=[
            ft.PieChartSection(
                SrSent["Positive"],
                color=ft.colors.GREEN,
                radius=90,
                border_side=ft.BorderSide(0, ft.colors.with_opacity(0, ft.colors.WHITE)),
                title="Positive",
                title_style=ft.TextStyle(color=color30)
            ),
            ft.PieChartSection(
                SrSent["Neutral"],
                color=ft.colors.YELLOW,
                radius=90,
                border_side=ft.BorderSide(0, ft.colors.with_opacity(0, ft.colors.WHITE)),
                title="Neutral",
                title_style=ft.TextStyle(color=color30)
            ),
            ft.PieChartSection(
                SrSent["Negative"],
                color=ft.colors.RED,
                radius=90,
                border_side=ft.BorderSide(0, ft.colors.with_opacity(0, ft.colors.WHITE)),
                title="Negative",
                title_style=ft.TextStyle(color=color30)
            ),
        ],
        sections_space=1,
        center_space_radius=0,
        expand=True,
    ),ft.Column([
        ft.Text(size=40,color=color30,value="Service Feedbacks"),
        ft.Text(size=40,color=color30,value=f"No of. Positive Responses: {SrSent['Positive']}"),
        ft.Text(size=40,color=color30,value=f"No of. Neutral Responses: {SrSent['Neutral']}"),
        ft.Text(size=40,color=color30,value=f"No of. Negative Responses: {SrSent['Negative']}")])]))
        PRFEEDK=ft.Container(width=1000,
        content=ft.Row(alignment=ft.MainAxisAlignment.CENTER,controls=[ft.PieChart(
        sections=[
            ft.PieChartSection(
                PrSent["Positive"],
                color=ft.colors.GREEN,
                radius=90,
                border_side=ft.BorderSide(0, ft.colors.with_opacity(0, ft.colors.WHITE)),
                title="Positive",
                title_style=ft.TextStyle(color=color30)
            ),
            ft.PieChartSection(
                PrSent["Neutral"],
                color=ft.colors.YELLOW,
                radius=90,
                border_side=ft.BorderSide(0, ft.colors.with_opacity(0, ft.colors.WHITE)),
                title="Neutral",
                title_style=ft.TextStyle(color=color30)
            ),
            ft.PieChartSection(
                PrSent["Negative"],
                color=ft.colors.RED,
                radius=90,
                border_side=ft.BorderSide(0, ft.colors.with_opacity(0, ft.colors.WHITE)),
                title="Negative",
                title_style=ft.TextStyle(color=color30)
            ),
        ],
        sections_space=1,
        center_space_radius=0,
        expand=True,
    ),ft.Column([
        ft.Text(size=40,color=color30,value=f"{PRFD} Reviews"),
        ft.Text(size=40,color=color30,value=f"No of. Positive Responses: {PrSent['Positive']}"),
        ft.Text(size=40,color=color30,value=f"No of. Neutral Responses: {PrSent['Neutral']}"),
        ft.Text(size=40,color=color30,value=f"No of. Negative Responses: {PrSent['Negative']}"),
    ])]))
        PRODPRF=ft.Container(width=1000,alignment=ft.alignment.top_center,content=ft.DataTable(
            columns=[ft.DataColumn(ft.Text("ProductName",color=color30,size=35)),ft.DataColumn(ft.Text("No.of People Who Preferred",size=35,color=color30))],
            rows=fetchProductpreferencesfromDb() if survey_isrunn() else []
        ))
        AnalyticaPane=ft.Container(ft.Column(controls=[RATINGB,SRVFDBK,PRFEEDK,PRODPRF],spacing=10,scroll=ft.ScrollMode.HIDDEN),height=600,width=1200,alignment=ft.alignment.top_center)
        Home.content=ft.Column([ft.Text(value=StoreName,size=90,color=color30),ft.Text(value=f"{Backend.welmsg(name)}",size=40,color=color30),AnalyticaPane],horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        SRSTAT=survey_isrunn()
        match SRSTAT:
            case True:
                pass
            case False:
                AnalyticaPane.content=ft.Column([ft.Text("No Survey is Running",color=color10,size=75,text_align=ft.TextAlign.CENTER),ft.Text("Go to Survey Info to Post A Survey",color=color30,size=55,text_align=ft.TextAlign.CENTER)],spacing=20,alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                page.update()
        page.update()
    def e2(e):
        def surcre(e):
            ICUR.execute(f'USE {Base}')
            try:
                ICUR.execute(f"insert into surveytablelog values ({int(getSID())},NULL,'{str(dt.datetime.now().date())}','{str(dt.datetime.now().time())}',NULL,NULL, \"{PTY.value}\",\"{PFD.value}\",1)")
            except errors.IntegrityError:
                page.snack_bar=ft.SnackBar(content=ft.Text(f"SURVEYID {int(getSID())} HAS BEEN ALREADY USED. TRY A DIFFERENT NUMBER"))
                page.snack_bar.open=True
                page.update()
            except ValueError:
                page.snack_bar=ft.SnackBar(content=ft.Text(f"INVALID SURVEYID. ENTER A PROPER NUMBER !"))
                page.snack_bar.open=True
                page.update()
            else:
                ICUR.execute(f"create table opensurvey (SERVFDB text,SRVRATN int,PRODPREF text,PRODFED text)")
                DBInstanc.commit()
                page.snack_bar=ft.SnackBar(ft.Text("Survey Posted"))
                page.snack_bar.open=True
                page.dialog.open=False
                page.update()
            Home.content=ft.Text(color=color30,value="Click Surveys to Refresh")
            page.update()     
        def setqns(e):
            def clsdl(e):
                creationdialog.open=0
                page.update()
            for key in X:
                for el in X[key]:
                    el=ft.dropdown.Option(el)
                key=ft.dropdown.Option(key)
            def Items():
                D=[]
                for i in X.values():
                    for j in i:
                        D.append(j)
                return D
            global PTY,PFD
            PTY=ft.Dropdown(label="Select ProductType",options=list(X.keys()))
            PFD=ft.Dropdown(label="Select ProductName",options=Items())
            global SID
            SID=ft.TextField(width=300,max_length=5)
            Config=ft.Container(ft.Column([ft.Text("Enter Survey Number"),SID,ft.Text("Select The Name of Product You Want to Know About Public's Preference"),PTY,ft.Text("Select The Type of Product You Want to Get Public's Feedback"),PFD],scroll=ft.ScrollMode.HIDDEN),width=300,height=300)
            Table=ft.Column([Config,ft.Row([ft.ElevatedButton(text="Create Survey",on_click=surcre),ft.ElevatedButton(text="Cancel",on_click=clsdl)])])
            page.update()
            creationdialog=ft.AlertDialog(title=ft.Text('Create Survey',color=color30),actions=[Table])
            page.dialog=creationdialog
            creationdialog.open=True
            page.update()
        SurveyNoMsg=ft.Column(
            [
                ft.Text(
                    value="No Information about Survey",
                    size=50,
                    color=color30
                    ),
                ft.ElevatedButton(
                    "Create New",
                    height=90,
                    width=140,
                    on_click=setqns,
                    color=color30,
                    bgcolor=color10
                    )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        if not survey_isrunn():
            connectionrefresh()
            Home.content=SurveyNoMsg
            page.update()
        else:
            Home.content=ft.Column([ft.Text(
                value=f"{count()} Responses Received",
                size=50,
                color=color30
                )
                ,ft.ElevatedButton(
                    
                    text="Stop Collecting Responses",
                    on_click=e0,
                    color=color30
                    )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            page.update()            
        page.update()
    def submit(e):
        print('USER IS ADMIN:',user_is_admin)
        def clsban(e):
            page.banner.open=False
            page.update()
        match user_is_admin:
            case True:
                page.banner=ft.Banner(content=ft.Text("Survey Submit Button Submits Your Response"),actions=[ft.TextButton(text="Close",on_click=clsban)])
                page.banner.open=True
                page.update()
            case False:
                Not_Filled=(SerFD.value==None)|(SerRat.value==None)|(PrdFD.value==None)|(PrdPRE.value==None)
                match Not_Filled:
                    case False:
                        connectionrefresh()
                        ICUR.execute(f'insert into opensurvey values ("{SerFD.value}",{SerRat.value},"{PrdPRE.value}","{PrdFD.value}")')
                        DBInstanc.commit()
                        connectionrefresh()
                        Home.content=ft.Text(weight=30,size=90,value="Thank You for Giving Feedback!")
                        page.floating_action_button=ft.FloatingActionButton(text="Go Back",on_click=kmod)
                        page.update()
                    case True:
                        page.banner=ft.Banner(content=ft.Text("Every Field is Required"),actions=[ft.TextButton(text="Close",on_click=clsban)])
                        page.banner.open=True
                        page.update()
    def e3(e):
        Home.content=None
        srvst=survey_isrunn()
        match srvst:
            case True:
                def clearresp(e):
                    SerFD.value=SerRat.value=PrdFD.value=PrdPRE.value=None
                    page.update()
                page.floating_action_button=ft.FloatingActionButton(text="Clear",on_click=clearresp)
                ICUR.execute(f"select producttype from surveytablelog where Survid={getSID()}")
                PTYP=ICUR.fetchall()[0][0]
                global SerRat,SerFD,PrdFD,PrdPRE
                ICUR.execute(f"select productname from surveytablelog where Survid={getSID()}")
                PRFD=ICUR.fetchall()[0]
                SerRat=ft.Dropdown(options=[ft.dropdown.Option('1'),ft.dropdown.Option('2'),ft.dropdown.Option('3'),ft.dropdown.Option('4'),ft.dropdown.Option('5')],color=color30,border_color=color30,width=600)
                SerFD=ft.TextField(border_color=color30,color=color30,width=600)
                PrdFD=ft.TextField(border_color=color30,color=color30,width=600)
                PrdPRE=ft.Dropdown(options=LoadObjectPs(PTYP),color=color30,width=600,border_color=color30)
                SurveyCol=ft.Column([
                ft.Text(f"Give Feedback about Our Service",size=40,color=color30),
                SerFD,
                ft.Text("Rate Our Service from 1 to 5",size=40,color=color30),
                SerRat,
                ft.Text(f"Give Feedback about {PRFD[0]}",size=40,color=color30),
                PrdFD,
                ft.Text(f"Which {PTYP} Would You Prefer The Most?",size=40,color=color30),
                PrdPRE,
                ft.ElevatedButton(text="Submit Survey",on_click=submit,bgcolor=color10,color=color30)
                ],alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER,spacing=30,scroll=ft.ScrollMode.HIDDEN)
                Home.content=SurveyCol
                page.update()
            case False:
                match user_is_admin:
                    case True:
                        page.floating_action_button=None
                        page.update()
                    case False:
                        page.floating_action_button=ft.FloatingActionButton(text="Refresh",on_click=kmod)
                        page.update()
                Home.content=ft.Container(ft.Column([
                    ft.Text(StoreName,
                            color=color10,
                            size=75,
                            text_align=ft.TextAlign.CENTER),
                    ft.Text(f"{Backend.getdate()} | {Backend.fetchtime()}",
                            color=color30,
                            size=55,
                            text_align=ft.TextAlign.CENTER)],
                            spacing=20,
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER))
                page.update()
    def e5(e):
        Home.content=ft.Text(
            value="Logout",
            size=50,
            color=color30
            )
        page.update()
    def e6(e):
        Home.content=ft.Text(
            value="Quitting Application...",
            size=50,
            color=color30
            )
        page.update()
        time.sleep(1)
        page.window_destroy()
    def e7(e):
        def delsurvey(e):
            def clsdlg(e):
                surveyid.open=False
                page.update()
                global Surn
                ICUR.execute(f'select surveyname from {Base}.surveytablelog where survid={int(Survid.value)}')
                Surn=str(ICUR.fetchall()[0][0]).replace(' ','_')
                ICUR.execute(f'delete from surveytablelog where survid={int(Survid.value)}')
                DBInstanc.commit()
                connectionrefresh()
                ICUR.execute(f'drop table closedsurvey_{Surn}')
                DBInstanc.commit()
                connectionrefresh()
                Home.content=ft.Text(color=color30,value="Click Survey Log to Refresh")
                page.update()
            Survid=ft.TextField(label="Type.",width='500',border_color=color30,color=color30,on_submit=clsdlg)
            surveyid=ft.AlertDialog(content=ft.Text(color=color30,value="Enter SurveyID to Confirm",size=35),actions=[Survid],actions_alignment=ft.MainAxisAlignment.CENTER)
            page.dialog=surveyid
            surveyid.open=True
            page.update()
            connectionrefresh()
        ICUR.execute(f'select SurvID,SurveyName,DateOfCreation,TimeofCreation,DateOfTermination,TimeofTermination from {Base}.surveytablelog where openonrt=0')
        Surveys=ICUR.fetchall()
        def review(e):
            def clsdlg(e):
                ICUR.execute(f'select surveyname from {Base}.surveytablelog where survid={int(Survid.value)}')
                Surn=str(ICUR.fetchall()[0][0]).replace(' ','_')
                Surtblname=f'closedsurvey_{Surn}'
                surveyid.open=False
                ICUR.execute(f'select productname from {Base}.surveytablelog where survid={int(Survid.value)}')
                PRFD=ICUR.fetchall()[0][0]
                e2(None)
                Home.content=None
                Home.alignment=ft.alignment.center
                page.update()
                Wordcloud(src=fetchServiceFeedbacksfromDB(Surtblname),path='./SubFiles/sfgraph.png',Title="Service Feedback")
                Srvcld=ft.Container(image_src='./SubFiles/sfgraph.png',height=350,width=350)
                Wordcloud(src=fetchProdFeedbacksfromDB(Surtblname),path='./SubFiles/pfgraph.png',Title=f"{PRFD} Feedback")
                Prdcld=ft.Container(image_src='./SubFiles/pfgraph.png',height=350,width=350)
                SentimentPlot(data=SentimentScore(fetchProdFeedbacksfromDB(Surtblname)),path='./SubFiles/pfplot.png',Title="Product Feedback")
                PFSplt=ft.Container(image_src='./SubFiles/pfplot.png',height=350,width=350)
                SentimentPlot(data=SentimentScore(fetchServiceFeedbacksfromDB(Surtblname)),path='./SubFiles/sfplot.png',Title="Service Feedback")
                SFSplt=ft.Container(image_src='./SubFiles/sfplot.png',height=350,width=350)
                BarPlot(fetchRatingsfromDB(Surtblname),path='./SubFiles/ratebr.png',Title="Star Rating")
                RaPlt=ft.Container(image_src='./SubFiles/ratebr.png',height=350,width=350)
                BarPlot(fetchProductpreferencesfromDb(Surtblname,sid=int(Survid.value)),path='./SubFiles/prodbr.png',Title="Star Rating")
                PPPlt=ft.Container(image_src='./SubFiles/prodbr.png',height=350,width=350)
                Home.content=ft.Container(width=1200,height=800,content=ft.Column(
                        scroll=ft.ScrollMode.ADAPTIVE,
                        controls=[
                            ft.Row(
                                [
                                    Srvcld,
                                    SFSplt,
                                    

                                ]                                
                            ),
                            ft.Row(
                                [
                                    Prdcld,
                                    PFSplt
                                    
                                ]
                            ),
                            ft.Row(
                                [
                                    PPPlt,
                                    RaPlt
                                    
                                ]
                            )
                        ]
                    ))
                page.update()
            Survid=ft.TextField(label="Type.",width='500',border_color=color30,color=color30,on_submit=clsdlg)
            surveyid=ft.AlertDialog(content=ft.Text(color=color30,value="Enter SurveyID to Confirm",size=35),actions=[Survid],actions_alignment=ft.MainAxisAlignment.CENTER)
            page.dialog=surveyid
            surveyid.open=True
            page.update()
            connectionrefresh()
        def ConverttoDatarow(ls):
            O=[]
            for i in ls :
                o=ft.DataRow()                    
                for j in i:# ls is [el1,el2,el3] --> [datacel1,datacel2...n]
                    j=ft.DataCell(ft.Text(j))
                    o.cells.append(j)
                o.cells.append(ft.DataCell(content=ft.Row([ft.ElevatedButton(text="Delete",on_click=delsurvey),ft.ElevatedButton(text="Review",on_click=review)])))
                O.append(o)
            print(O) 
            return O
        Log=ft.DataTable(
            columns=[ft.DataColumn(ft.Text("SURVEYID")),ft.DataColumn(ft.Text("SURVEY NAME")),ft.DataColumn(ft.Text("Date Created")),ft.DataColumn(ft.Text("Time Created")),ft.DataColumn(ft.Text("Date Closed")),ft.DataColumn(ft.Text("Time Closed")),ft.DataColumn(ft.Text("Options"))]
            ,rows=ConverttoDatarow(Surveys),width=1000)
        Home.content=Log
        page.update()
    def e0(e):
        def e8(e):
            surveyname.open=False
            page.update()
            global surn
            surn=surveyname.actions[0].value
            Survey=str(surn).title()
            global ICUR
            global DBInstanc
            try:
                ICUR.execute(f"alter table opensurvey rename to closedsurvey_{str(surn).replace(' ','_')}")
                DBInstanc.commit()
                connectionrefresh()
            except errors.ProgrammingError:
                page.snack_bar=ft.SnackBar(content=ft.Text("Name Already Exists. Try With Different One.."))
                page.snack_bar.open=True
                page.update()
            ICUR.execute(f"update surveytablelog set SurveyName='{Survey}' where SurvID={getSID()}")
            DBInstanc.commit()
            connectionrefresh()
            ICUR.execute(f"update surveytablelog set DateofTermination='{str(dt.datetime.now().date())}' where SurvID={int(getSID())}")
            DBInstanc.commit()
            connectionrefresh()
            ICUR.execute(f"update surveytablelog set TimeofTermination='{str(dt.datetime.now().time())}' where SurvID={int(getSID())}")
            DBInstanc.commit()
            connectionrefresh()
            ICUR.execute(f"update surveytablelog set openonrt=0 where survid={getSID()}")
            DBInstanc.commit()
            connectionrefresh()
            surveyname.open=False
            Home.content=ft.Text(color=color30,value="Click Surveys to Refresh")
            page.update()
        surveyname=ft.AlertDialog(content=ft.Text(color=color30,value="Save Survey As",size=35),actions=[ft.TextField(label="Your Surveyname",width='500',border_color=color30,color=color30,on_submit=e8)],actions_alignment=ft.MainAxisAlignment.CENTER)
        page.dialog=surveyname
        surveyname.open=True
        page.update()
    def kmod(e):
        connectionrefresh()
        KiosOpt.disabled=False
        LoginOpt.disabled=True
        e3(e=None)
        page.appbar=None
        page.update()
    def get_user_passwd():
        ICUR.execute(f'select userid from {Base}.credtable')
        Users = ICUR.fetchall()
        ICUR.execute(f'select password from {Base}.credtable')
        Password=ICUR.fetchall()
        CredRel={}
        for i in range(len(Users)):
            CredRel[Users[i][0]]=Password[i][0]
        return CredRel
    def getupced(e):
        def check_creds(e):
            try:
                global PSD
                PSD=CredRel[UID.value]
            except KeyError:
                page.snack_bar=ft.SnackBar(content=ft.Text("Choose a UserName!"))
                page.snack_bar.open=True
                page.update()
            if PSD==PAS.value:
                print("Correct Password")
                DashOpt.disabled=False
                LoginOpt.disabled=True
                KiosOpt.disabled=False
                global user_is_admin
                user_is_admin=True
                SurLog.disabled=False
                SurvOpt.disabled=False
                page.snack_bar=ft.SnackBar(ft.Text("Correct Credentials Entered"))
                page.snack_bar.open=True
                Home.content=None
                page.update()
                ICUR.execute(f'use {Base}')
                ICUR.execute(f'select username from credtable where userid = "{UID.value}"')
                global name
                name=ICUR.fetchall()[0][0]
                page.update()
                Welcome=BasicUtils()
                shutter=ft.AnimatedSwitcher(
                    Home,
                    transition=ft.AnimatedSwitcherTransition.FADE,
                    duration=500,
                    reverse_duration=500,
                    switch_in_curve=ft.AnimationCurve.EASE_IN,
                    switch_out_curve=ft.AnimationCurve.EASE_IN_OUT
                )
                global sleep
                def sleep(e):
                    if shutter.content==Home:
                        global rel
                        rel=ft.Stack(controls=[ft.Image(src='./Subfiles/sleep.jpg'),ft.Row(alignment=ft.CrossAxisAlignment.CENTER,vertical_alignment=ft.MainAxisAlignment.CENTER,controls=[ft.Text(Welcome.welmsg(name),color=ft.colors.with_opacity(0.5,color30),size=70)])])
                        shutter.content=rel
                        page.appbar=None
                        page.update()
                    else:
                        shutter.content=Home
                        page.appbar=Controls
                        page.update()
                page.add(shutter)
                page.floating_action_button=ft.FloatingActionButton(width=90,content=ft.Row([ft.Icon(ft.icons.NIGHTLIFE,color=color30),ft.Text("Relax",color=color30)]),bgcolor=ft.colors.TRANSPARENT,on_click=sleep)  
            else:
                print("Wrong Password")
                page.snack_bar=ft.SnackBar(ft.Text("Wrong Credentials Entered.Try Again"))
                page.snack_bar.open=True
                page.update()
        CredRel=get_user_passwd()
        Users = list(CredRel.keys())
        for user in range(len(Users)):
            Users[user]=ft.dropdown.Option(Users[user])
        UID=ft.Dropdown(
            options=Users,
            width=500,
            color=color30,
            label="User ID",
            label_style=ft.TextStyle(color=color30))
        PAS=ft.TextField(
            label='Password',
            width=500,
            border_color=color30,
            color=color30,
            password=True,
            on_submit=check_creds)
        Kiosk=ft.ElevatedButton(
            text="Open As Kiosk",
            bgcolor=color10,
            color=color30,
            on_click=kmod)
        LoginPan=ft.Column([
            ft.Text(
                "Login",
                size=90,
                color=color30
                ),UID,PAS,Kiosk]
                ,alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER)        
        Home.content=LoginPan
        page.update()
    Home=ft.Container(  
        border_radius=ft.border_radius.all(30),
        width=1500,
        alignment=ft.alignment.center,
        height=900,
        content=None)
    global Controls
    Controls=ft.AppBar(
        leading=ft.Icon(ft.icons.SHOP),
        leading_width=40,
        title=ft.Text("Sentiment Analysis"),
        bgcolor=ft.colors.with_opacity(0.5,ft.colors.BLACK),
        color=color10,
        toolbar_height=35,
        actions=[
            ft.ElevatedButton(icon=ft.icons.LOGIN,on_click=getupced,text="Login",color=color30,bgcolor=ft.colors.with_opacity(0,ft.colors.TRANSPARENT)),
            ft.ElevatedButton(icon=ft.icons.ASSESSMENT,on_click=e1,text="Dashboard",disabled=True,color=color30,bgcolor=ft.colors.with_opacity(0,ft.colors.TRANSPARENT)),
            ft.ElevatedButton(icon=ft.icons.DOCUMENT_SCANNER,on_click=e2,text="Survey Info",disabled=True,color=color30,bgcolor=ft.colors.with_opacity(0,ft.colors.TRANSPARENT)),
            ft.ElevatedButton(icon=ft.icons.ASSIGNMENT,on_click=e7,text="Survey Log",disabled=True,color=color30,bgcolor=ft.colors.with_opacity(0,ft.colors.TRANSPARENT)),
            ft.ElevatedButton(icon=ft.icons.REMOVE_RED_EYE,on_click=e3,text="Kiosk Preview",disabled=True,color=color30,bgcolor=ft.colors.with_opacity(0,ft.colors.TRANSPARENT)),
            ft.ElevatedButton(icon=ft.icons.EXIT_TO_APP,on_click=e6,text="Exit",color=color30,bgcolor=ft.colors.with_opacity(0,ft.colors.TRANSPARENT)),
        ]
    )
    page.appbar=Controls
    LoginOpt=page.appbar.actions[0]
    DashOpt=page.appbar.actions[1]
    SurvOpt=page.appbar.actions[2]
    SurLog=page.appbar.actions[3]
    KiosOpt=page.appbar.actions[4]
    Dashboard=ft.Container(
        padding=15,
        expand=True,
        content=Home)
    page.add(Dashboard)
    page.update()
def setupetaapp():
    ICUR.execute("SHOW DATABASES")
    DBS=ICUR.fetchall()
    DBEX=''
    for Bases in DBS:
        for SBASES in Bases:
            DBEX+=SBASES
    if 'store_' not in DBEX:
        os.system('cls')
        WEL_TXT = f'''
        WELCOME TO STORE ASSISTANT :)
            - A SMALL TOOL TO ASSIST YOU FOR GOOD :)
        SETUP PAGE INSTANCE [ONE-TIME] CREATED ON {dt.datetime.now()}
    '''
        print(WEL_TXT)
        storedb = str(input('STAGE 1 -> ENTER THE NAME OF YOUR STORE -> ').replace(' ','0'))
        ICUR.execute(f'create database store_{storedb}')
        ICUR.execute(f'use store_{storedb}')
        if DBInstanc.is_connected():
            print(F"BACKEND CONNECTION ESTABLISHED SUCCESSFULLY ON {dt.datetime.now()}")
            path = input("""STAGE 2 -> \nNOTE THAT IN ORDER TO USE THIS SOFTWARE, YOU'LL NEED TO HAVE A CSV FILE CONTAINING LIST
OF ITEMNAME, ITEMTYPE [ORDER MAINTAINED AS GIVEN] .\n
CONSIDERING THAT YOU HAVE ONE SUCH FILE RIGHT NOW, YOU ARE EXPECTED TO PASTE ITS FILE PATH
OVER HERE: """)
            with open(path) as src:
                Data = csv.reader(src)
                Stock = []
                for record in Data:
                    Stock.append(record)
                Stock.remove([ 'ItemType','ItemName'])
                if ['', ' ', '', '', ''] in Stock:
                    Stock.remove(['', ' ', '', '', ''])                # data purification 
            ICUR.execute('create table StockTable (ItemNo int,ItemType text,ItemName text )')
            print("STOCKTABLE CREATION SUCCESSFULL")
            DBInstanc.commit()
            i=1
            for rows in Stock:
                ICUR.execute(f'insert into StockTable Values({i},"{rows[0]}","{rows[1]}")')
                DBInstanc.commit()
            print("LIST UPDATED TO STOCKTABLE")
            print("Stage 3 -> Admin Credentials")
            userid = input("""THOUGH WE ARE HERE TO ASSIST YOU, WE NEED AN ADMINISTRATOR FOR THIS APPLICATION TO MANAGE THE DATA, CREATE A NEW SURVEY,
AND TROUBLESHOOT PROBLEMS AND ERRORS THAT KICK IN. \n ENTER YOUR USERID OVER HERE: """)
            pwd = input("SET ADMIN PASSWORD: ")
            cnfstat=1
            while cnfstat:
                print("PASSWORD NOT CONFIRMED DUE TO MISMATCH OR 1STINSTANCE")
                CNFPWD = input("CONFIRM PASSWORD: ")
                if pwd == CNFPWD:
                    print(F"PASSWORD {pwd} IS CONFIRMED")
                    cnfstat=0
            name = input("WE CAN'T ALWAYS REFER YOU WITH YOUR USER-ID. SO LET US KNOW YOUR NAME PLEASE: ")
            ICUR.execute('create table CredTable(UNO int,USERNAME text,UserID text,Password text)')
            DBInstanc.commit()
            ICUR.execute(f'insert into Credtable values(0,"{name}","{userid}","{pwd}")')
            DBInstanc.commit()
            ICUR.execute('create table surveytablelog (SurvID int(5) primary key,SurveyName text,DateOfCreation date,TimeofCreation time,DateOfTermination date,TimeofTermination time,ProductType text,ProductName text,OPENONRT int(1))')
            DBInstanc.commit()
            print("SETUP COMPLETED. YOU ARE ALL SET")
        else:
            print(f"BACKEND CONNECTION FAILED")
    else:
        def fetchDB():
            found_db=False
            ICUR.execute('show databases')
            DBS=ICUR.fetchall()
            while not found_db:
                for Base in DBS:
                    if 'store_' in Base[0]:
                        found_db=True
                        return Base[0] 
        os.system('cls')
        global Base
        Base=fetchDB()
        global ItemMapSql
        def ItemMapSql(base=Base,cursor=ICUR,table='stocktable'):
            with open("./Subfiles/ObjPersist.dat",'wb') as ObjectPersistence:
                cursor.execute(f'use {base}')
                cursor.execute(f'select distinct(itemtype) from {table}')
                D=cursor.fetchall()
                S=[]
                for i in D:
                    S.append(i[0])
                R={}
                for ψ in S:
                    R[ft.dropdown.Option(ψ)]=[]
                for ζ in R:
                    cursor.execute(f'select itemname from {table} where itemtype="{ζ.key}"')
                    T=[]
                    for i in cursor.fetchall():
                        T.append(ft.dropdown.Option(i[0]))
                    R[ζ]=T
                pickle.dump(R,ObjectPersistence)
            return R
        global LoadObjectPs
        def LoadObjectPs(key):
            with open("./Subfiles/ObjPersist.dat",'rb') as ObjectPersistence:
                X=pickle.load(ObjectPersistence)
                for i in X:
                    if i.key == key:
                        return X[i]
        global StoreName
        StoreName=Base.replace('store_','').replace('_',' ').replace('0',' ').title()
        print("DETECTED STOREDB - INITIATING UI")
        print(f"UI SESSION STARTED ON {Backend.today().upper()} ")
        ft.app(target=AdminUI)
        print(f"UI SESSION ENDED ON {Backend.today().upper()} ")
setupetaapp()
print("PROGRAM EXITED")
