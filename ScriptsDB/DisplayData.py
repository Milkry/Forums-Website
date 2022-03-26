import sqlite3

db = sqlite3.connect("forums.db")
cursor = db.cursor()

#cursor.execute("insert into user (userName, passwordHash, isAdmin, creationTime, lastVisit) values ('TestUser1', 12345, 0, 1, 1);")
#cursor.execute("delete from user where userName='TestUser1';")
#db.commit()

query = """
  select * from user;
"""

results = cursor.execute(query)

for row in results:
    print(row)

db.close()
