from flask import Flask, jsonify, redirect, session, url_for, render_template
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = b'jGqNj?O}&6n<]&}mG+nS)([Smk6{P>k5>F^d:qJ2&z:qZQf}blH0=bm/my"&(]-'

# Make a json config file to store the database name
PATH = "./ScriptsDB/forums.db"


@app.errorhandler(404)
def page_not_found(e):
    return NotFound()


@app.route('/')
def homepage():
    topics = getAllTopics()
    if isUserLoggedIn():
        username = getUsername(getUserIDFromSession())
        return render_template("Homepage.html", loggedIn=True, username=username, topics=topics)
    return render_template("Homepage.html", topics=topics)


################################ Account System ################################
@app.route('/register/<username>/<password>', methods=["POST"])
def register(username, password):
    if username and password and not isUserLoggedIn():
        db = sqlite3.connect(PATH)
        cursor = db.cursor()
        # Determine if the account exists
        accoundFound = False
        account = cursor.execute(
            "select userID from user where userName=?", (username,))
        for row in account:
            accoundFound = True
        # If it does, then return an error and let the user know. Else create it.
        if accoundFound:
            return 'USER_EXISTS'
        else:
            cursor.execute(
                "insert into user (userName, passwordHash, isAdmin, creationTime, lastVisit) values (?, ?, 0, 1, 1)", (username, password,))
            newAccount = cursor.execute(
                "select userID from user where userName=?", (username,))
            for row in newAccount:
                session["userID"] = row[0]
            db.commit()
            db.close()
            return 'USER_CREATED'
    return 'MISSING_DATA'


@app.route('/login/<username>/<password>', methods=["POST"])
def login(username, password):
    if username and password and not isUserLoggedIn():
        db = sqlite3.connect(PATH)
        cursor = db.cursor()
        account = cursor.execute(
            "select userID, passwordHash from user where userName=?", (username,))
        # If the for loop doesn't get executed, then the account doesn't exist
        for user in account:
            if user[1] == password:
                session["userID"] = user[0]
                db.close()
                return 'LOGIN_SUCCESSFUL'
            else:
                db.close()
                return 'LOGIN_FAILED_PASSWORD'
        db.close()
        return 'LOGIN_FAILED_USERNAME'
    return 'MISSING_DATA'


@app.route('/logout')
def logout():
    if isUserLoggedIn():
        session.clear()
    return redirect(url_for("homepage"))
###############################################################################


# View a topic
@app.route('/<topicId>', methods=["GET"])
def displayTopic(topicId):
    db = sqlite3.connect(PATH)
    cursor = db.cursor()
    claimList = []
    if isTopicIdValid(topicId):
        claims = cursor.execute(
            "select * from claim where topic=?", (topicId,))
        for row in claims:
            claimId = row[0]
            claimList.append(claimId)
        topicName = getTopicName(topicId)
        if isUserLoggedIn():
            username = getUsername(getUserIDFromSession())
            return render_template("Claims.html", loggedIn=True, username=username, topicId=topicId, topicName=topicName, claims=claimList)
        else:
            return render_template("Claims.html", topicId=topicId, topicName=topicName, claims=claimList)
    else:
        return NotFoundMessage("Topic")


# Creates a topic
@app.route('/topic/create/<topicName>', methods=["POST"])
def createTopic(topicName):
    if isUserLoggedIn():
        db = sqlite3.connect(PATH)
        cursor = db.cursor()
        cursor.execute("insert into topic (topicName, postingUser, creationTime, updateTime) values (?, ?, 0, 0)",
                       (topicName, getUserIDFromSession(),))
        db.commit()
        db.close()
        return 'TOPIC_CREATED'
    return 'MISSING_DATA'


# View a claim
@app.route('/<topicId>/<claimId>', methods=["GET"])
def displayClaim(topicId, claimId):
    return NotFoundMessage("Claim")


# Page to write and submit your claim
@app.route('/<topicId>/claim/new', methods=["GET"])
def newClaim(topicId):
    if isTopicIdValid(topicId):
        if isUserLoggedIn():
            return render_template("NewClaim.html", topicId=topicId)
        else:
            return redirect(url_for("homepage"))
    return NotFound()


# Creates a claim
# app.route...


####################################################################
######################### HELPER FUNCTIONS #########################
####################################################################

# Returns true if the user is currently logged in and false if not
def isUserLoggedIn():
    if session.get("userID"):
        return True
    return False


# Returns the userID from the browser session
def getUserIDFromSession():
    return session.get("userID")


# Returns the username of the user when logged in
def getUsername(id):
    db = sqlite3.connect(PATH)
    cursor = db.cursor()
    user = cursor.execute(
        "select userName from user where userID=?", (id,))
    for row in user:
        username = row[0]
    db.close()
    return username


# Returns a json string with all the topics in the database
def getAllTopics():
    db = sqlite3.connect(PATH)
    cursor = db.cursor()
    topics = cursor.execute("select topicName from topic")
    topicList = []
    for row in topics:
        topicList.append(row[0])
    db.close()
    return topicList


# Error 404 page with a custom content missing message
def NotFoundMessage(content):
    return render_template("404.html", content=content)


# Default error 404 page
def NotFound():
    return render_template("404.html", content="Page")


# Returns true if the topicId given exists in the database and false if not
def isTopicIdValid(Id):
    db = sqlite3.connect(PATH)
    cursor = db.cursor()
    topic = cursor.execute("select * from topic where topicID=?", (Id,))
    for row in topic:
        db.close()
        return True
    db.close()
    return False


# Returns topic name based on the topicId
def getTopicName(Id):
    db = sqlite3.connect(PATH)
    cursor = db.cursor()
    topic = cursor.execute(
        "select topicName from topic where topicID=?", (Id,))
    for row in topic:
        db.close()
        return row[0]
    db.close()
    return "NULL"
