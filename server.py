from flask import Flask, redirect, session, url_for, render_template
import sqlite3

app = Flask(__name__)
app.secret_key = b'jGqNj?O}&6n<]&}mG+nS)([Smk6{P>k5>F^d:qJ2&z:qZQf}blH0=bm/my"&(]-'

# Make a json config file to store the database name
PATH = "./ScriptsDB/forums.db"


@app.route('/')
def homepage():
    if isUserLoggedIn():
        username = getUsername(getUserIDFromSession())
        return render_template("homepage.html", loggedIn=True, username=username)
    return render_template("homepage.html")


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


def getUsername(id):
    db = sqlite3.connect(PATH)
    cursor = db.cursor()
    user = cursor.execute(
        "select userName from user where userID=?", (id,))
    for row in user:
        username = row[0]
    db.close()
    return username
