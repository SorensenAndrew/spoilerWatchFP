from flask import Flask
from flask import redirect
from flask import request
from flask import render_template
from flask import session
from collections import OrderedDict
from flask import jsonify
import urllib
import json
import pprint
import hashlib
import mysql.connector
from urllib2 import urlopen
from urllib2 import Request
from json import load
from lxml import html
import requests


app = Flask(__name__)
app.secret_key = "4321"

@app.route('/')
def index():
    return redirect('/login')

###### News Feed #####

@app.route('/home')
def navhome():
    name = session["username"]
    db = mysql.connector.connect(user='b31545577f01ed', password='7bc97660',host='DATABASE_URL', database='heroku_0762eace2527e49', port='8889')
    cursor = db.cursor()
    cursor.execute("select * from showData where username!='"+ name + "' order by dateAdded desc")
    showdata = cursor.fetchall()
    return render_template('userHome.html',showdata=showdata)


###########################


@app.route('/login', methods=['post','get'])
def login():
    return render_template('login.html')

@app.route('/users')
def users():
    db = mysql.connector.connect(user='b31545577f01ed', password='7bc97660',host='DATABASE_URL', database='heroku_0762eace2527e49', port='8889')
    cursor = db.cursor()
    cursor.execute("select * from users")
    data = cursor.fetchall()
    return render_template('users.html',data=data)

###### Display Shows #######################
@app.route('/shows')
def show():
    name = session["username"]
    db = mysql.connector.connect(user='b31545577f01ed', password='7bc97660',host='DATABASE_URL', database='heroku_0762eace2527e49', port='8889')
    cursor = db.cursor()
    cursor.execute("select showName, showTitle, showSeason, showEpisode,episodeCount from showData where username='"+ name+ "'")
    showdata = cursor.fetchall()
    return render_template('shows.html',showdata=showdata)

#### Show Progress and Badges ####

@app.route('/badges', methods=['post','get'])
def badgePage():
    name = session["username"]
    showName = request.form['showName']
    db = mysql.connector.connect(user='b31545577f01ed', password='7bc97660',host='DATABASE_URL', database='heroku_0762eace2527e49', port='8889')
    cursor = db.cursor()
    cursor.execute("select showName, showTitle, showSeason, showEpisode,episodeCount, plot, airDate from showData where showName='" + showName + "' and username='" + name + "'")
    showdata = cursor.fetchall()
    badgeCursor = db.cursor()
    badgeCursor.execute("select showName, badges from badges where showName='" + showName + "' and username='" + name + "'")
    badgeData = badgeCursor.fetchall()
    return render_template('badges.html',showdata=showdata, badgeData = badgeData)

### Show All Badges Page #####

@app.route('/allBadges', methods=['get'])
def allBadges():
    name = session["username"]
    db = mysql.connector.connect(user='b31545577f01ed', password='7bc97660',host='DATABASE_URL', database='heroku_0762eace2527e49', port='8889')
    badgeCursor = db.cursor()
    badgeCursor.execute("select badges from badges where username='" + name + "'")
    badgeData = badgeCursor.fetchall()
    return render_template('allBadges.html', badgeData = badgeData)

###### Verify user login ######

@app.route('/checklogin', methods=['post','get'])
def checklogin():
    session["username"] = request.form["username"]
    session["password"] = request.form["password"]
    db = mysql.connector.connect(user='b31545577f01ed', password='7bc97660',host='DATABASE_URL', database='heroku_0762eace2527e49', port='8889')
    cursor = db.cursor()
    hashval = hashlib.md5(request.form["password"]).hexdigest()

    cursor.execute("select * from users where username=%s and password=%s", (session["username"], session["password"]))
    data = cursor.fetchall()
    if data:
        data = {"username":session["username"],"password":session["password"]}
        return render_template('showSearch.html',data=data)
    else:
        return redirect('/login')

#### Friends List and Management ########

@app.route('/friendForm', methods=['post','get'])
def friendForm():
    return render_template('addFriend.html')

@app.route('/addFriend', methods=['post','get'])
def addfriend():
    name = session["username"]
    friend = request.form['Addfriend']
    db = mysql.connector.connect(user='b31545577f01ed', password='7bc97660',host='DATABASE_URL', database='heroku_0762eace2527e49', port='8889')
    cursor = db.cursor()
    cursor.execute("insert into friends(username1, username2)values(%s,%s)", (name, friend))
    db.commit()
    return redirect('/friends')

@app.route('/friends')
def friends():
    name = session["username"]
    db = mysql.connector.connect(user='b31545577f01ed', password='7bc97660',host='DATABASE_URL', database='heroku_0762eace2527e49', port='8889')
    cursor = db.cursor()
    cursor.execute("select username1, username2 from friends where username1='"+ name+ "'")
    data = cursor.fetchall()
    return render_template('friends.html',data=data)

@app.route('/manageFriends', methods=['post', 'get'])
def friendmanager():
    name = session["username"]
    db = mysql.connector.connect(user='b31545577f01ed', password='7bc97660',host='DATABASE_URL', database='heroku_0762eace2527e49', port='8889')
    cursor = db.cursor()
    cursor.execute("select username1, username2 from friends where username1='"+ name+ "'")
    data = cursor.fetchall()
    return render_template('manageFriends.html',data=data)

@app.route('/friendData',methods=['post', 'get'])
def frienddata():
    friendname = request.form['friend']
    db = mysql.connector.connect(user='b31545577f01ed', password='7bc97660',host='DATABASE_URL', database='heroku_0762eace2527e49', port='8889')
    cursor = db.cursor()
    cursor.execute("select showName, showTitle, showSeason, showEpisode from showData where username='" + friendname + "'")
    data = cursor.fetchall()
    badgeCursor = db.cursor()
    badgeCursor.execute("select badges from badges where username='" + friendname + "'")
    badgeData = badgeCursor.fetchall()
    return render_template('friendData.html',data=data, badgeData=badgeData)

@app.route('/deleteFriends', methods=['post', 'get'])
def deletefriend():
    name = session["username"]
    friendname = request.form['friend']
    db = mysql.connector.connect(user='b31545577f01ed', password='7bc97660',host='DATABASE_URL', database='heroku_0762eace2527e49', port='8889')
    cursor = db.cursor()
    cursor.execute("delete from friends where username2='" + friendname + "' and username1='"+ name+ "'")
    db.commit()
    return render_template('deleteConf.html')


######## User Registration ########

@app.route('/newUser')
def newUser():
    return render_template('addUserform.html')


@app.route('/addUser',methods=['post', 'get'])
def addUser():
    uname = request.form['newUser']
    upass = request.form['newPassword']
    db = mysql.connector.connect(user='b31545577f01ed', password='7bc97660',host='DATABASE_URL', database='heroku_0762eace2527e49', port='8889')
    cursor = db.cursor()
    cursor.execute("select username from users")
    users = cursor.fetchall()
    print users
    cursor2 = db.cursor()
    cursor2.execute("insert into users(username, password)values(%s,%s)", (uname, upass))
    db.commit()
    return redirect('/login')


################### Add Show ###################################################################

@app.route('/parseJSON',methods=['post', 'get'])
def parseJSON():
    name = session["username"].title()
    title = request.form["title"].title()
    season = request.form['season']
    episode = request.form['episode']
    url = "http://www.omdbapi.com/?t=" + title +"&Season="+ season + "&Episode=" + episode +"&r=json"
    url = url.replace(" ","%20")
    loadurl = urllib.urlopen(url)
    data = json.loads(loadurl.read().decode(loadurl.info().getparam('charset') or 'utf-8'))
    url2 = "http://www.omdbapi.com/?t=" + title +"&Season="+ season +"&r=json"
    url2 = url2.replace(" ","%20")
    loadurl2 = urllib.urlopen(url2)
    data2 = json.loads(loadurl2.read().decode(loadurl2.info().getparam('charset') or 'utf-8'))
    episodeCount = []
    episodeCount.append(data2['Episodes'])
    for i in range(len(episodeCount)):
        print len(episodeCount[i])
    totalEpisodes = len(episodeCount[i])
    episodedata = data['Episode']
    titledata = data['Title']
    seasondata= data['Season']
    plotData = data['Plot']
    airDate = data['Released']
    tE = int(totalEpisodes)
    eD = int(episodedata)
    db = mysql.connector.connect(user='b31545577f01ed', password='7bc97660',host='DATABASE_URL', database='heroku_0762eace2527e49', port='8889')
    cursor = db.cursor()
    cursor.execute("insert into showData(username, showTitle, showSeason, showEpisode, showName, episodeCount, plot, airDate)values(%s,%s,%s,%s,%s, %s, %s, %s)", (name, titledata, seasondata, episodedata, title, totalEpisodes, plotData, airDate))
    cursor2 = db.cursor()
    cursor2.execute("select showEpisode, episodeCount from showData where showName='" + title + "'")
    new_count = cursor2.fetchall()
    if eD == tE:
        badge = "You have completed season '" + season + "' of '" + title + "'"
        cursor3 = db.cursor()
        cursor3.execute("insert into badges(username, showSeason, showName, badges)values(%s,%s,%s,%s)", (name, season, title, badge))
    cursor4 = db.cursor()
    cursor4.execute("select showName from showData where username='" + name + "'")
    totalShowsFollowed = cursor4.fetchall()
    if len(totalShowsFollowed) == 5:
        showNumberBadge = "Following 5 Shows!"
        cursor5 = db.cursor()
        cursor5.execute("insert into badges(username, badges)values(%s,%s)", (name, showNumberBadge))
    elif len(totalShowsFollowed) == 10:
        showNumberBadge = "Following 10 Shows!"
        cursor5 = db.cursor()
        cursor5.execute("insert into badges(username, badges)values(%s,%s)", (name, showNumberBadge))
    elif len(totalShowsFollowed) == 15:
        showNumberBadge = "Following 15 Shows!"
        cursor5 = db.cursor()
        cursor5.execute("insert into badges(username, badges)values(%s,%s)", (name, showNumberBadge))
    elif len(totalShowsFollowed) == 20:
        showNumberBadge = "Following 20 Shows!"
        cursor5 = db.cursor()
        cursor5.execute("insert into badges(username, badges)values(%s,%s)", (name, showNumberBadge))
    elif len(totalShowsFollowed) == 25:
        showNumberBadge = "Following 25 Shows!"
        cursor5 = db.cursor()
        cursor5.execute("insert into badges(username, badges)values(%s,%s)", (name, showNumberBadge))
    db.commit()
    return render_template('profilePage.html',data=data,newVar=new_count)


@app.route('/showSearch')
def nprForm():
    return render_template('showSearch.html')


@app.route('/deleteShow', methods=['post', 'get'])
def deleteshow():
    name = session["username"]
    random = request.form["random"]
    db = mysql.connector.connect(user='b31545577f01ed', password='7bc97660',host='DATABASE_URL', database='heroku_0762eace2527e49', port='8889')
    cursor = db.cursor()
    cursor.execute("delete from showData where showName='" + random + "' and username='" + name + "'")
    db.commit()
    return redirect('/shows')

@app.route('/form')
def form():
    return render_template('form.html')

### Javascript Fetch Data ####

@app.route('/dataRoute', methods=['get'])
def dataRoute():
    name = session["username"]
    db = mysql.connector.connect(user='b31545577f01ed', password='7bc97660',host='CLEARDB_DATABASE_URL', database='heroku_0762eace2527e49', port='8889')
    cursor2 = db.cursor2()
    cursor2.execute("select showName, showEpisode, episodeCount from showData where username='" + name + "'")
    newVar = cursor2.fetchall()
    print newVar
    return  render_template('shows.html')

# where username='" + name + "' and showName='" + showName + "'" #

#### Show Update ###########

@app.route('/updateShow', methods=['post', 'get'])
def updateshow():
    name = session["username"]
    title = request.form["title"]
    season = request.form['season']
    episode = request.form['episode']
    url = "http://www.omdbapi.com/?t=" + title +"&Season="+ season + "&Episode=" + episode +"&r=json"
    url = url.replace(" ","%20")
    loadurl = urllib.urlopen(url)
    data = json.loads(loadurl.read().decode(loadurl.info().getparam('charset') or 'utf-8'))
    episodedata = data['Episode']
    eD = int(episodedata)
    titledata = data['Title']
    seasondata= data['Season']
    plotdata = data['Plot']
    airdatedata = data['Released']
    db = mysql.connector.connect(user='b31545577f01ed', password='7bc97660',host='DATABASE_URL', database='heroku_0762eace2527e49', port='8889')
    cursor = db.cursor()
    cursor.execute("update showData set showTitle=%s, showSeason=%s, showEpisode=%s, plot=%s, airDate=%s where showName='" + title + "' and username='" + name  + "'", (titledata, seasondata, episodedata, plotdata, airdatedata ))
    cursor2 = db.cursor()
    cursor2.execute("select showEpisode, episodeCount, plot, airDate from showData where showName='" + title + "'")
    new_count = cursor2.fetchall()
    cursor3 = db.cursor()
    cursor3.execute("select episodeCount from showData where showName='" + title + "'")
    testvar = cursor3.fetchone()
    tE = testvar[0]
    if eD == tE:
        badge = "You have completed season '" + season + "' of '" + title + "'"
        cursor3 = db.cursor()
        cursor3.execute("insert into badges(username, showSeason, showName, badges)values(%s,%s,%s,%s)", (name, season, title, badge))
    db.commit()
    return render_template('profilePage.html',data=data, newVar=new_count)


######### Logout ###############

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

############################

@app.route('/formtest', methods=['post','get'])
def formtest():
    userinput = request.form["user"]
    hashed = hashlib.md5(userinput).hexdigest()
    return hashed

######################################## MOVIE SECTIONS ###################################################

# @app.route('/movieToggle')
# def movieToggle():
#     return render_template('moviesHome.html')
#
# @app.route('/movies')
# def movies():
#     return render_template('movies.html')
#
# @app.route('/addMovies', methods=['post','get'])
# def addMovies():
#     name = session["username"].title()
#     title = request.form["title"].title()
#     url = "http://www.omdbapi.com/?t=" + title+"&r=json"
#     url = url.replace(" ","%20")
#     loadurl = urllib.urlopen(url)
#     data = json.loads(loadurl.read().decode(loadurl.info().getparam('charset') or 'utf-8'))
#     year = data['Year']
#     rating = data['Rated']
#     plot = data['Plot']
#     actors = data['Actors']
#     writer = data['Writer']
#     director = data['Director']
#     genre = data['Genre']
#     awards = data['Awards']
#     db = mysql.connector.connect(user='b31545577f01ed', password='7bc97660',host='DATABASE_URL', database='heroku_0762eace2527e49', port='8889')
#     cursor = db.cursor()
#     cursor.execute("insert into movieData(username, movieTitle, movieYear, genre, rating, director, writer, actor, awards, plot)values(%s,%s,%s,%s,%s, %s, %s, %s, %s, %s)", (name, title, year, genre, rating, director, writer, actors, awards, plot))
#     cursor2 = db.cursor()
#     cursor2.execute("select showEpisode, episodeCount from showData where showName='" + title + "'")
#     new_count = cursor2.fetchall()
#     cursor4 = db.cursor()
#     cursor4.execute("select movieTitle from movieData where username='" + name + "'")
#     totalMoviesFollowed = cursor4.fetchall()
#     if len(totalMoviesFollowed) == 5:
#         movieNumberBadge = "Following 5 Movies!"
#         cursor5 = db.cursor()
#         cursor5.execute("insert into badges(username, badges)values(%s,%s)", (name, movieNumberBadge))
#     elif len(totalMoviesFollowed) == 10:
#         movieNumberBadge = "Following 10 Movies!"
#         cursor5 = db.cursor()
#         cursor5.execute("insert into badges(username, badges)values(%s,%s)", (name, movieNumberBadge))
#     elif len(totalMoviesFollowed) == 15:
#         movieNumberBadge = "Following 15 Movies!"
#         cursor5 = db.cursor()
#         cursor5.execute("insert into badges(username, badges)values(%s,%s)", (name, movieNumberBadge))
#     elif len(totalMoviesFollowed) == 20:
#         movieNumberBadge = "Following 20 Movies!"
#         cursor5 = db.cursor()
#         cursor5.execute("insert into badges(username, badges)values(%s,%s)", (name, movieNumberBadge))
#     elif len(totalMoviesFollowed) == 25:
#         movieNumberBadge = "Following 25 Movies!"
#         cursor5 = db.cursor()
#         cursor5.execute("insert into badges(username, badges)values(%s,%s)", (name, movieNumberBadge))
#     db.commit()
#     return render_template('addMovies.html', data=data)



if __name__ == '__main__':
    app.run(debug = True)