import sqlite3

db = sqlite3.connect("forums.db")
cursor = db.cursor()

query = """
  select * from topic;
"""

results = cursor.execute(query)

for row in results:
    print(row)

db.close()
