import sqlite3

db = sqlite3.connect("forums.db")
cursor = db.cursor()

table = int(input(
    "(1)user (2)topic (3)claim (4)claimToClaimType (5)claimToClaim (6)replyText (7)replyToClaimType (8)replyToClaim (9)replyToReplyType (10)replyToReply: "))

if table == 1:
    table = "user"
elif table == 2:
    table = "topic"
elif table == 3:
    table = "claim"
elif table == 4:
    table = "claimToClaimType"
elif table == 5:
    table = "claimToClaim"
elif table == 6:
    table = "replyText"
elif table == 7:
    table = "replyToClaimType"
elif table == 8:
    table = "replyToClaim"
elif table == 9:
    table = "replyToReplyType"
elif table == 10:
    table = "replyToReply"
else:
    print("Invalid input.")
    quit()

results = cursor.execute("select * from " + table)
for row in results:
    print(row)
db.close()
