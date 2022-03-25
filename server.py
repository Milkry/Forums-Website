from flask import Flask, session, request, url_for, render_template
import sqlite3

app = Flask(__name__)
app.secret_key = b'jGqNj?O}&6n<]&}mG+nS)([Smk6{P>k5>F^d:qJ2&z:qZQf}blH0=bm/my"&(]-'

# Establish database connection
# Make a json config file to store the database name
db = sqlite3.connect("./ScriptsDB/forums.db")
cursor = db.cursor()


@ app.route('/')
def view():
    if isUserValid():
        return render_template("homepage.html")
    return "Not Okay..."


@ app.route('/register/account', methods=["POST"])
def newAccount():
    if "username" and "password" and "confirmPassword" in request.form:
        # check if these credentials are already in the database
        # if not then go ahead create the account using cookies and store in database too
        return 'Ok!'
    return 'Not okay...'


#################
### FUNCTIONS ###
#################

def isUserValid():
    print("isUserValid")
    return True
    # upon loading the site, we need to check
    # if user is logged in (check session)
    # then, render the homepage template using a jinja condition that displays the user account along with it
    # else again render the homepage template but without showing the account user (will show register/login)
