import pymysql,time
from socket import *

name="김휘"
songname = "mare moehhh"
score = 100

conn = pymysql.connect(host = "edu.gsa.hs.kr", port=18001, user="s17029", passwd="1111", db="s17029", charset="utf8")
cur = conn.cursor(pymysql.cursors.DictCursor)

def database():
    global name
    global songname
    global score
    query = "insert into rank(name,songname,score) values('"+name+"','"+songname+"',"+str(score)+")"
     
    cur.execute(query)
    conn.commit()

def deldatabase():
    
    query = "delete from rank"
    cur.execute(query)
    conn.commit()

def showdatabase():
    global name
    query = "select name, songname, score from rank"
    cur.execute(query)
    results = cur.fetchall()

    for row in results:
        print(row)

def getdata():
    global name
    global score
    maxscore=0
    query = "select name, songname, score from rank where name = '"+name+"'"
    cur.execute(query)
    results = cur.fetchall()

    for row in results:
        if row["songname"]==songname and row["name"]==name:
            if row["score"]>maxscore:
                maxscore=row["score"]
    if maxscore<score:
        database()
    return maxscore
showdatabase()
