import sqlite3

db = sqlite3.connect("forums.db")
cursor = db.cursor()

# Read the sql script
with open('dbSetup.sql', 'r') as sqlFile:
    script = sqlFile.read()

# Run it and commit it
print('<!> Creating a new database... <!>')
db.executescript(script)
db.commit()
db.close()
print('<!> Database successfully created! <!>')
