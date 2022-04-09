from flask import Flask, jsonify, redirect, session, url_for, render_template, request
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
        # Determine if the account already exists
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
                "insert into user (userName, passwordHash, isAdmin, creationTime, lastVisit) values (?, ?, 0, julianday('now'), 0)", (username, hashPassword(password),))
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
            if user[1] == hashPassword(password):
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


# When submitting a topic
@app.route('/new/topic/<topicName>', methods=["POST"])
def createTopic(topicName):
    if isUserLoggedIn():
        db = sqlite3.connect(PATH)
        cursor = db.cursor()
        cursor.execute("insert into topic (topicName, postingUser, creationTime, updateTime) values (?, ?, julianday('now'), 0)",
                       (topicName, getUserIDFromSession(),))
        db.commit()
        db.close()
        return 'TOPIC_CREATED'
    return 'MISSING_DATA'


# View a claim
@app.route('/<topicId>/<claimId>', methods=["GET"])
def displayClaim(topicId, claimId):
    if not isTopicIdValid(topicId):
        return NotFoundMessage("Topic")
    if not isClaimIdValid(claimId):
        return NotFoundMessage("Claim")
    if not isTopicRelatedToClaim(topicId, claimId):
        return NotFoundMessage("Claim is not related to that topic")

    db = sqlite3.connect(PATH)
    cursor = db.cursor()
    claim = cursor.execute(
        "select postingUser, text, creationTime from claim where claimID=?", (claimId,))
    for row in claim:
        userId = row[0]
        claimText = row[1]
        creationTime = convertJulianTime(row[2])
    username = getUsername(userId)
    topicName = getTopicName(topicId)
    db.close()
    return render_template("Claim.html", topicId=topicId, topicName=topicName, username=username, claimText=claimText, creationTime=creationTime, isAdmin=isAdmin(userId), loggedIn=True)


# Page to write and submit your claim
@app.route('/<topicId>/new/claim', methods=["GET"])
def newClaimPage(topicId):
    if isTopicIdValid(topicId):
        if isUserLoggedIn():
            topicName = getTopicName(topicId)
            return render_template("NewClaim.html", topicId=topicId, topicName=topicName, userId=getUserIDFromSession())
        else:
            # change it so it redirects you to login instead [CHANGE_NEEDED]
            return redirect(url_for("homepage"))
    return NotFoundMessage("Topic")


# When submitting a claim
@app.route('/<topicId>/<userId>/new', methods=["POST"])
def createClaim(topicId, userId):
    # This might need some testing, if a userid is not returned this might break the server? [CHANGE_NEEDED]
    if int(getUserIDFromSession()) != int(userId):
        return NotFoundMessage("UserId")
    if not isTopicIdValid(topicId):
        return NotFoundMessage("Topic")

    db = sqlite3.connect(PATH)
    cursor = db.cursor()
    cursor.execute("insert into claim (topic, postingUser, creationTime, updateTime, text) values (?, ?, julianday('now'), 0, ?)",
                   (topicId, userId, request.form["claimText"],))
    claim = cursor.execute(
        "select claimID from claim where text=?", (request.form["claimText"],))  # Instead of searching the database using the claimText, use the creationTime [CHANGE_NEEDED]
    for row in claim:
        claimId = row[0]
    if not claimId:
        # Handle the internal server error better here [CHANGE_NEEDED]
        db.close()
        return 'ClaimId was not initialized.'
    db.commit()
    db.close()
    updateTimeTopic(topicId)
    return redirect("/" + str(topicId) + "/" + str(claimId))


####################################################################
######################### HELPER FUNCTIONS #########################
####################################################################

# Returns a hashed password
def hashPassword(password):
    return hashlib.sha512(password.encode('utf-8')).hexdigest()


# Returns true if the user is currently logged in and false if not
def isUserLoggedIn():
    if session.get("userID"):
        return True
    return False


# Returns the userID from the browser session
def getUserIDFromSession():
    return session.get("userID")


# Returns the username of the user when logged in
# Instead of searching the database for the username, save it in the session and get it from there [CHANGE_NEEDED]
def getUsername(id):
    db = sqlite3.connect(PATH)
    cursor = db.cursor()
    user = cursor.execute(
        "select userName from user where userID=?", (id,))
    for row in user:
        username = row[0]
    db.close()
    return username


# Returns true if the user is an admin and false if not
def isAdmin(id):
    db = sqlite3.connect(PATH)
    cursor = db.cursor()
    user = cursor.execute(
        "select isAdmin from user where userID=?", (id,))
    for row in user:
        if row[0] == True:
            db.close()
            return True
        db.close()
        return False


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
def isTopicIdValid(id):
    db = sqlite3.connect(PATH)
    cursor = db.cursor()
    topic = cursor.execute("select * from topic where topicID=?", (id,))
    for row in topic:
        db.close()
        return True
    db.close()
    return False


# Returns topic name based on the topicId
def getTopicName(id):
    db = sqlite3.connect(PATH)
    cursor = db.cursor()
    topic = cursor.execute(
        "select topicName from topic where topicID=?", (id,))
    for row in topic:
        db.close()
        return row[0]
    db.close()
    return "NULL"


# Updates the "updateTime" column of a specific topic
def updateTimeTopic(topicId):
    db = sqlite3.connect(PATH)
    cursor = db.cursor()
    cursor.execute(
        "update topic set updateTime=julianday('now') where topicID=?", (topicId,))
    db.commit()
    db.close()


# Returns true if the claimId given exists in the database and false if not
def isClaimIdValid(id):
    db = sqlite3.connect(PATH)
    cursor = db.cursor()
    claim = cursor.execute("select * from claim where claimID=?", (id,))
    for row in claim:
        db.close()
        return True
    db.close()
    return False


# Returns true if the topic is related to a claim and false if not
def isTopicRelatedToClaim(topicId, claimId):
    db = sqlite3.connect(PATH)
    cursor = db.cursor()
    claim = cursor.execute(
        "select topic from claim where claimId=?", (claimId,))
    for row in claim:
        if int(topicId) == row[0]:
            db.close()
            return True
    db.close()
    return False


# Converts julian time to regular time and returns it
def convertJulianTime(julianTime):
    db = sqlite3.connect(PATH)
    cursor = db.cursor()
    time = cursor.execute("select datetime(?)", (julianTime,))
    for row in time:
        return row[0]
####################################################################
