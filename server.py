from flask import Flask, redirect, url_for, render_template, request, session
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = b'jGqNj?O}&6n<]&}mG+nS)([Smk6{P>k5>F^d:qJ2&z:qZQf}blH0=bm/my"&(]-'

# Make a json config file to store the database name
PATH = "./ScriptsDB/forums.db"

# IMPLEMENT LAST VISIT FOR USER [CHANGE_NEEDED]


@app.errorhandler(404)
def page_not_found(e):
    return NotFound()


# Home
@app.route('/')
def homepage():
    topics = getAllTopics()
    return render_template("Homepage.html", user=getUserStatus(), topics=topics)


# Register
@app.route('/register/<username>/<password>', methods=["POST"])
def register(username, password):
    if username and password and not isUserLoggedIn():
        db = sqlite3.connect(PATH)
        cursor = db.cursor()
        # Determine if the account already exists
        account = cursor.execute(
            "select userID from user where userName=?", (username,))
        for row in account:
            return 'USER_EXISTS'
        cursor.execute(
            "insert into user (userName, passwordHash, isAdmin, creationTime, lastVisit) values (?, ?, 0, julianday('now'), 0)", (username, hashPassword(password),))
        db.commit()
        newAccount = cursor.execute(
            "select userID from user where userName=?", (username,))
        for row in newAccount:
            session["userID"] = row[0]
            session["Username"] = username
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
@ app.route('/signout')
def signout():
    if isUserLoggedIn():
        session.clear()
    return redirect(url_for("homepage"))


# Admin Panel
@ app.route('/adminpanel', methods=["GET"])
def adminPanel():
    user = getUserStatus()
    if not user.LoggedIn:
        return redirect(url_for("homepage"))
    if not user.Admin:
        return redirect(url_for("homepage"))

    db = sqlite3.connect(PATH)
    cursor = db.cursor()
    admins = cursor.execute(
        "select userID, userName from user where isAdmin=1")
    adminList = []
    for row in admins:
        class Admin:
            Id = row[0]
            Username = row[1]
        adminList.append(Admin)
    return render_template("AdminPanel.html", user=user, admins=adminList)


# Adding an admin
@ app.route('/adminpanel/add', methods=["POST"])
def addAdmin():
    db = sqlite3.connect(PATH)
    cursor = db.cursor()
    username = request.form["adminUsername"]
    found = False
    account = cursor.execute("select userID from user where userName=?",
                             (username,))
    for row in account:
        found = True
    if found:
        cursor.execute("update user set isAdmin=1 where userName=?",
                       (username,))
        db.commit()
        db.close()
        return redirect(url_for("adminPanel"))
    return NotFoundMessage("Admin")


# Removing an admin
@ app.route('/adminpanel/remove/<adminId>', methods=["POST"])
def removeAdmin(adminId):
    if not isUserIdValid(adminId):
        return NotFoundMessage("User")
    if not isAdmin(adminId):
        return NotFoundMessage("Admin")

    db = sqlite3.connect(PATH)
    cursor = db.cursor()
    cursor.execute("update user set isAdmin=0 where userID=?", (adminId,))
    db.commit()
    db.close()
    return redirect(url_for("adminPanel"))


# View a topic
@ app.route('/<topicId>', methods=["GET"])
def displayClaimsOfTopic(topicId):
    user = getUserStatus()
    if not isTopicIdValid(topicId):
        return NotFoundMessage("Topic")

    db = sqlite3.connect(PATH)
    cursor = db.cursor()
    claimList = []
    claims = cursor.execute(
        "select claimID, postingUser, creationTime, updateTime, text from claim where topic=? order by updateTime desc", (topicId,))
    for row in claims:
        class Claim:
            Id = row[0]
            Username = getUsername(row[1])
            CreatedAt = convertJulianTime(row[2], "FULL")
            UpdatedAt = convertJulianTime(row[3], "FULL")
            Text = row[4][:25] + str("...")
        claimList.append(Claim)
    return render_template("Claims.html", user=user, topicId=topicId, topicName=getTopicName(topicId), claims=claimList)


# Submit a topic
@ app.route('/new/topic/<topicName>', methods=["POST"])
def createTopic(topicName):
    if isUserLoggedIn():
        db = sqlite3.connect(PATH)
        cursor = db.cursor()
        cursor.execute("insert into topic (topicName, postingUser, creationTime, updateTime) values (?, ?, julianday('now'), julianday('now'))",
                       (topicName, getUserIDFromSession(),))
        db.commit()
        db.close()
        return 'TOPIC_CREATED'
    return 'MISSING_DATA'


# View a claim
@ app.route('/<topicId>/<claimId>', methods=["GET"])
def displayClaim(topicId, claimId):
    user = getUserStatus()
    if not isTopicIdValid(topicId):
        return NotFoundMessage("Topic")
    if not isClaimIdValid(claimId):
        return NotFoundMessage("Claim")
    if not isTopicRelatedToClaim(topicId, claimId):
        return NotFoundMessage("Claim is not related to that topic")

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
    return render_template("Claim.html", user=user, topic=Topic, claim=Claim, replies=getAllReplies(claimId))


# Page to write a claim
@ app.route('/<topicId>/new/claim', methods=["GET"])
def newClaimPage(topicId):
    user = getUserStatus()
    if not isTopicIdValid(topicId):
        return NotFoundMessage("Topic")
    if not user.LoggedIn:
        return redirect(url_for("homepage"))

    topicName = getTopicName(topicId)
    return render_template("NewClaim.html", user=user, topicId=topicId, topicName=topicName, userId=getUserIDFromSession())


# Submit a claim
@ app.route('/<topicId>/<userId>/new', methods=["POST"])
def createClaim(topicId, userId):
    # This might need some testing, if a userid is not returned this might break the server? [CHANGE_NEEDED]
    if int(getUserIDFromSession()) != int(userId):
        return NotFoundMessage("UserId")
    if not isTopicIdValid(topicId):
        return NotFoundMessage("Topic")

    db = sqlite3.connect(PATH)
    cursor = db.cursor()
    text = request.form["claimText"]
    currentTime = getCurrentJulianTime()
    cursor.execute("insert into claim (topic, postingUser, creationTime, updateTime, text) values (?, ?, ?, ?, ?)",
                   (topicId, userId, currentTime, currentTime, text,))
    claim = cursor.execute(
        "select claimID from claim where creationTime=?", (currentTime,))  # Instead of searching the database using the claimText, use the creationTime [CHANGE_NEEDED]
    for row in claim:
        claimId = row[0]
    cursor.execute(
        "update topic set updateTime=julianday('now') where topicID=?", (topicId,))
    db.commit()
    db.close()
    return redirect("/" + str(topicId) + "/" + str(claimId))


# Submit a reply to a claim
@ app.route('/<topicId>/<claimId>/new/reply', methods=["POST"])
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
@ app.route('/<topicId>/<claimId>/new/reply/<parentId>', methods=["POST"])
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
    for row in Id:
        replyId = row[0]
    cursor.execute("insert into replyToReply (reply, parent, replyToReplyRelType) values (?, ?, ?)",
                   (replyId, parentId, replyType,))
    db.commit()
    cursor.execute(
        "update claim set updateTime=julianday('now') where claimID=?", (claimId,))
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


# Returns basic variables for the navigation bar
def getUserStatus():
    if isUserLoggedIn():
        username = getUsername(getUserIDFromSession())
        loggedIn = True
        admin = isAdmin(getUserIDFromSession())
    else:
        username = "NULL"
        loggedIn = False
        admin = False

    class Status:
        Username = username
        LoggedIn = loggedIn
        Admin = admin
    return Status


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


# Returns true if userId is in the database and false if not
def isUserIdValid(id):
    db = sqlite3.connect(PATH)
    cursor = db.cursor()
    user = cursor.execute(
        "select userName from user where userID=?", (id,))
    for row in user:
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


# Returns the total amount of claims a topic has
def getTotalClaimsInTopic(topicId):
    db = sqlite3.connect(PATH)
    cursor = db.cursor()
    claim = cursor.execute(
        "select count(*) from claim where topic=?", (topicId,))
    for row in claim:
        return row[0]


# Returns the newest/latest claim created in a topic
def getLatestClaimInTopic(topicId):
    db = sqlite3.connect(PATH)
    cursor = db.cursor()
    latestClaim = cursor.execute(
        "select claimID, postingUser, updateTime from claim where topic=? order by updateTime desc limit 1", (topicId,))

    class LatestClaim:
        HasClaim = False
    for row in latestClaim:
        class LatestClaim:
            HasClaim = True
            Id = row[0]
            Username = getUsername(row[1])
            UpdatedAt = convertJulianTime(row[2], "FULL")
    return LatestClaim


# Returns all the topics available
def getAllTopics():
    db = sqlite3.connect(PATH)
    cursor = db.cursor()
    topics = cursor.execute(
        "select topicID, topicName, postingUser from topic order by updateTime desc")
    topicList = []
    for row in topics:
        topicId = row[0]
        topicName = row[1]
        poster = row[2]

        class Topic:
            Id = topicId
            Name = topicName
            Creator = getUsername(poster)
            Claims = getTotalClaimsInTopic(Id)
            Claim = getLatestClaimInTopic(Id)
        topicList.append(Topic)

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
        "select reply from replyToClaim where claim=?", (claimId,))
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
            ReplyType = getReplyType(Id, "CLAIM")
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
            ReplyType = getReplyType(Id, "REPLY")
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


# Returns the reply type text (Clarification/Counterargument/Evidence/Support/etc.)
def getReplyType(replyId, typeOfReply):
    if str(typeOfReply).upper() == "CLAIM":
        db = sqlite3.connect(PATH)
        cursor = db.cursor()
        type = cursor.execute(
            "select replyToClaimRelType from replyToClaim where reply=?", (replyId,))
        for row in type:
            typeId = row[0]
        claimType = cursor.execute(
            "select claimReplyType from replyToClaimType where claimReplyTypeID=?", (typeId,))
        for row in claimType:
            return row[0]
    elif str(typeOfReply).upper() == "REPLY":
        db = sqlite3.connect(PATH)
        cursor = db.cursor()
        type = cursor.execute(
            "select replyToReplyRelType from replyToReply where reply=?", (replyId,))
        for row in type:
            typeId = row[0]
        replyType = cursor.execute(
            "select replyReplyType from replyToReplyType where replyReplyTypeID=?", (typeId,))
        for row in replyType:
            return row[0]
    else:
        return "INVALID TYPE"


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
