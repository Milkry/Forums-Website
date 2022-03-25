import sqlite3

db = sqlite3.connect("forums.db")
cursor = db.cursor()

# Read the sql script
with open('dbReset.sql', 'r') as sqlFile:
    script = sqlFile.read()

# Run it and commit it
print('<!> Deleting database... <!>')
db.executescript(script)
db.commit()
db.close()
print('<!> Database successfully deleted! <!>')
