from flask import Flask, redirect, url_for, render_template, request, session
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = b'jGqNj?O}&6n<]&}mG+nS)([Smk6{P>k5>F^d:qJ2&z:qZQf}blH0=bm/my"&(]-'

# Make a json config file to store the database name
PATH = "./ScriptsDB/forums.db"


@app.errorhandler(404)
def page_not_found(e):
    return NotFound()


# Home
@app.route('/')
def homepage():
    topics = getAllTopics()
    if isUserLoggedIn():
        return render_template("Homepage.html", loggedIn=True, username=session["Username"], topics=topics)
    return render_template("Homepage.html", topics=topics)


# Register
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
                session["Username"] = getUsername(row[0])
            db.commit()
            db.close()
            return 'USER_CREATED'
    return 'MISSING_DATA'


# Login
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
                session["Username"] = getUsername(user[0])
                db.close()
                return 'LOGIN_SUCCESSFUL'
            else:
                db.close()
                return 'LOGIN_FAILED_PASSWORD'
        db.close()
        return 'LOGIN_FAILED_USERNAME'
    return 'MISSING_DATA'


# Logout
@app.route('/logout')
def logout():
    if isUserLoggedIn():
        session.clear()
    return redirect(url_for("homepage"))


# View a topic
@app.route('/<topicId>', methods=["GET"])
def displayClaimsOfTopic(topicId):
    if not isTopicIdValid(topicId):
        return NotFoundMessage("Topic")
    if isUserLoggedIn():
        loggedIn = True
    else:
        loggedIn = False

    db = sqlite3.connect(PATH)
    cursor = db.cursor()
    claimList = []
    claims = cursor.execute(
        "select claimID from claim where topic=?", (topicId,))
    for row in claims:
        claimId = row[0]
        claimList.append(claimId)
    return render_template("Claims.html", loggedIn=True, topicId=topicId, topicName=getTopicName(topicId), claims=claimList)


# Submit a topic
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
    if isUserLoggedIn():
        loggedIn = True
    else:
        loggedIn = False

    db = sqlite3.connect(PATH)
    cursor = db.cursor()
    # ADD UPDATE TIME WHEN A REPLY IS POSTED [CHANGE_NEEDED]
    claim = cursor.execute(
        "select postingUser, text, creationTime from claim where claimID=?", (claimId,))
    for row in claim:
        userId = row[0]
        claimText = row[1]
        creationTime = row[2]

    class Topic:
        TopicId = topicId
        TopicName = getTopicName(TopicId)

    class Claim:
        Username = getUsername(userId)
        ClaimId = claimId
        ClaimText = claimText
        JoinDate = getUserJoinDate(userId)
        ClaimPostDate = convertJulianTime(creationTime, "DATE")
        TotalPosts = getUserTotalPosts(userId)
        IsAdmin = isAdmin(userId)
        LastUpdateTime = getClaimLastUpdateTime(ClaimId)

    db.close()
    return render_template("Claim.html", topic=Topic, claim=Claim, replies=getAllReplies(claimId), loggedIn=loggedIn)


# Page to write a claim
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


# Submit a claim
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


# Submit a reply to a claim
@app.route('/<topicId>/<claimId>/new/reply', methods=["POST"])
def newClaimReply(topicId, claimId):
    if not isTopicIdValid(topicId):
        return NotFoundMessage("Topic")
    if not isClaimIdValid(claimId):
        return NotFoundMessage("Claim")
    if not isUserLoggedIn():
        return NotFoundMessage("Account")

    db = sqlite3.connect(PATH)
    cursor = db.cursor()
    replyText = request.form["replyToClaimText"]
    replyType = request.form["replyToClaimType"]
    creationTime = getCurrentJulianTime()

    cursor.execute("insert into replyText (postingUser, creationTime, text) values (?, ?, ?)",
                   (getUserIDFromSession(), creationTime, replyText,))
    db.commit()
    Id = cursor.execute(
        "select replyTextID from replyText where creationTime=?", (creationTime,))
    for row in Id:
        replyId = row[0]
    cursor.execute("insert into replyToClaim (reply, claim, replyToClaimRelType) values (?, ?, ?)",
                   (replyId, claimId, replyType,))
    db.commit()
    cursor.execute("update claim set updateTime=? where claimID=?",
                   (creationTime, claimId,))
    db.commit()
    db.close()
    return redirect("/" + str(topicId) + "/" + str(claimId))


# Submit a reply to a reply
@app.route('/<topicId>/<claimId>/new/reply/<parentId>', methods=["POST"])
def newReplyToReply(topicId, claimId, parentId):
    if not isTopicIdValid(topicId):
        return NotFoundMessage("Topic")
    if not isClaimIdValid(claimId):
        return NotFoundMessage("Claim")
    # Validate replyToID [CHANGE_NEEDED]
    # if not isReplyToIdValid(parentId):
    #    return NotFoundMessage("")
    if not isUserLoggedIn():
        return NotFoundMessage("Account")

    db = sqlite3.connect(PATH)
    cursor = db.cursor()
    replyText = request.form["replyToReplyText"]
    replyType = request.form["replyToReplyType"]
    creationTime = getCurrentJulianTime()

    cursor.execute("insert into replyText (postingUser, creationTime, text) values (?, ?, ?)",
                   (getUserIDFromSession(), creationTime, replyText))
    db.commit()
    Id = cursor.execute(
        "select replyTextID from replyText where creationTime=?", (creationTime,))
    replyId = 0
    for row in Id:
        replyId = row[0]
    cursor.execute("insert into replyToReply (reply, parent, replyToReplyRelType) values (?, ?, ?)",
                   (replyId, parentId, replyType,))
    db.commit()
    db.close()
    return redirect("/" + str(topicId) + "/" + str(claimId))


######################### HELPER FUNCTIONS #########################
# Error 404 page with a custom content missing message
def NotFoundMessage(content):
    return render_template("404.html", content=content)


# Default error 404 page
def NotFound():
    return render_template("404.html", content="Page")


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
            return True
        return False


# Returns the date when the account was created
def getUserJoinDate(id):
    db = sqlite3.connect(PATH)
    cursor = db.cursor()
    date = cursor.execute(
        "select creationTime from user where userID=?", (id,))
    for row in date:
        return convertJulianTime(row[0], "DATE")
    return "User doesn't exist"


# Returns the total number of posts and replies the user has created
def getUserTotalPosts(id):
    db = sqlite3.connect(PATH)
    cursor = db.cursor()
    amount = cursor.execute(
        "select count(*) from replyText where postingUser=?", (id,))
    for row in amount:
        return row[0]
    return -1


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


# Returns the text of a parent id
def getParentDetails(replyId):
    db = sqlite3.connect(PATH)
    cursor = db.cursor()
    # Gets parent id first
    parent = cursor.execute(
        "select parent from replyToReply where reply=?", (replyId,))
    for row in parent:
        parentId = row[0]
    # Get details of parent
    parentDetails = cursor.execute(
        "select * from replyText where replyTextID=?", (parentId,))
    for row in parentDetails:
        class Parent:
            Id = row[0]
            UserId = row[1]
            CreatedAt = row[2]
            Text = row[3]
        return Parent
    return "PARENT NOT FOUND"


# Returns true if a reply of a reply is related to a claim, false if not
def isReplyRelatedToClaim(replyTextId, claimId):
    db = sqlite3.connect(PATH)
    cursor = db.cursor()

    found = False
    STOP = False
    while not STOP:
        # Get parent Id
        parentId = -1
        reply = cursor.execute(
            "select parent from replyToReply where reply=?", (replyTextId,))
        for row in reply:  # Executes once
            parentId = row[0]
        print("Processing parentId[" + str(parentId) + "]")
        # If parentId is -1 then this replyTextId is not even in the replyToReply table
        # which means its a claim reply not a reply to reply. Therefore we should just stop as its not related
        if parentId == -1:
            found = False
            STOP = True

        # Get the claimId of the reply
        claim = cursor.execute(
            "select claim from replyToClaim where reply=?", (parentId,))
        # Executes once
        # If the for loop doesnt execute then this is not a claim reply, so theres more ancestors
        # Therefore we replace the replyTextId with the current parentId and we re-do the process
        # until we find a parent that is a claim reply, which will contain a claimId
        for row in claim:
            id = row[0]
            print("Found a claimId..." + str(id) +
                  ". Now will compare ClaimId[" + str(claimId) + "] == id[" + str(id) + "]")
            if int(claimId) == int(id):
                found = True
                STOP = True
            else:
                found = False
                STOP = True
        replyTextId = parentId

    print(found)
    if found:
        return True
    return False


# Returns a list of all the replies relating to a claimId
def getAllReplies(claimId):
    db = sqlite3.connect(PATH)
    cursor = db.cursor()
    replyList = []  # This list will contain all the replies

    allClaimReplies = cursor.execute(
        "select reply from replyToClaim where claim=?", (claimId,))  # Grab the reply type as well and showcase it [CHANGE_NEEDED]
    temp = []
    for row in allClaimReplies:
        temp.append(row[0])

    # Get all claim reply details
    for cId in temp:  # For every claim reply
        reply = cursor.execute(
            "select postingUser, creationTime, text from replyText where replyTextID=?", (cId,))
        for row in reply:  # Executes once
            userId = row[0]
            createdAt = row[1]
            text = row[2]

        class ClaimReply:
            isReplyToReply = False
            Id = cId
            Text = text
            Username = getUsername(userId)
            JoinDate = getUserJoinDate(userId)
            ReplyPostDate = convertJulianTime(createdAt, "DATE")
            TotalPosts = getUserTotalPosts(userId)
            IsAdmin = isAdmin(userId)
        replyList.append(ClaimReply)

    # Get all replies of replies related to the claim
    allRepliesOfReplies = cursor.execute("select reply from replyToReply")
    temp = []
    for row in allRepliesOfReplies:  # For every reply of reply
        print("Checking for..." + str(row[0]))
        if isReplyRelatedToClaim(row[0], claimId):
            temp.append(row[0])

    for rId in temp:  # For every reply of reply
        data = cursor.execute(
            "select postingUser, creationTime, text from replyText where replyTextID=?", (rId,))
        for row in data:  # Executes once
            userId = row[0]
            createdAt = row[1]
            text = row[2]
        parent = getParentDetails(rId)

        class ReplyReply:
            isReplyToReply = True
            Id = rId
            Text = text
            ReplyingToId = parent.Id
            ReplyingToUsername = getUsername(parent.UserId)
            ReplyingToText = parent.Text
            Username = getUsername(userId)
            JoinDate = getUserJoinDate(userId)
            ReplyPostDate = convertJulianTime(createdAt, "DATE")
            TotalPosts = getUserTotalPosts(userId)
            IsAdmin = isAdmin(userId)
        replyList.append(ReplyReply)

    return replyList


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


# Returns the date and time of when a claim was last updated
def getClaimLastUpdateTime(claimId):
    db = sqlite3.connect(PATH)
    cursor = db.cursor()
    date = cursor.execute(
        "select updateTime from claim where claimID=?", (claimId,))
    for row in date:
        return convertJulianTime(row[0], "FULL")


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
def convertJulianTime(julianTime, format):
    db = sqlite3.connect(PATH)
    cursor = db.cursor()
    if str(format).upper() == "FULL":
        time = cursor.execute("select datetime(?)", (julianTime,))
    elif str(format).upper() == "DATE":
        time = cursor.execute("select date(?)", (julianTime,))
    elif str(format).upper() == "TIME":
        time = cursor.execute("select time(?)", (julianTime,))
    else:
        return "Invalid"
    for row in time:
        return row[0]


# Returns the current date and time in julian form (Useful when needing to store it in variables)
def getCurrentJulianTime():
    db = sqlite3.connect(PATH)
    cursor = db.cursor()
    datetime = cursor.execute("select julianday('now')")
    for row in datetime:
        return row[0]
####################################################################
