from flask import Flask, jsonify, session, request, url_for, render_template
import sqlite3

app = Flask(__name__)
app.secret_key = b'jGqNj?O}&6n<]&}mG+nS)([Smk6{P>k5>F^d:qJ2&z:qZQf}blH0=bm/my"&(]-'

# Make a json config file to store the database name
PATH = "./ScriptsDB/forums.db"


@app.route('/')
def view():
    if isUserValid():
        return render_template("homepage.html")
    return "Not Okay..."


@app.route('/register/account/<username>/<password>', methods=["POST"])
def newAccount(username, password):
    """if username and password:
        db = sqlite3.connect(PATH)
        cursor = db.cursor()

        accoundFound = False
        account = cursor.execute(
            "select userID from user where userName=?", (username,))
        for row in account:
            accoundFound = True

        # If a record was found, then...
        if accoundFound:
            print("Account found! Aborting...")
            return {'ERROR': 'USER_EXISTS'}
        else:
            print("Creating a new account...")
            cursor.execute(
                "insert into user (userName, passwordHash, isAdmin, creationTime, lastVisit) values (?, ?, 0, 1, 1)", (username, password,))
            db.commit()
            db.close()
            return {'SUCCESS': 'USER_CREATED'}
"""
    return {'SUCCESS': 'USER_CREATED'}
    # if not then go ahead create the account using cookies and store in database too


####################################################################
######################### HELPER FUNCTIONS #########################
####################################################################

def isUserValid():
    return True
    # upon loading the site, we need to check
    # if user is logged in (check session)
    # then, render the homepage template using a jinja condition that displays the user account along with it
    # else again render the homepage template but without showing the account user (will show register/login)
