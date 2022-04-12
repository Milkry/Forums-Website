import sqlite3

db = sqlite3.connect("forums.db")
cursor = db.cursor()

user = input("Enter a username to make admin: ")

cursor.execute("update user set isAdmin=1 where userName=?", (user,))
db.commit()
db.close()
print("User given admin permissions.")
