import sqlite3

db = sqlite3.connect("forums.db")
cursor = db.cursor()

table = -1
print("Choose a table to display:")
while table != 0:
    table = int(input(
        "(1)user \n(2)topic \n(3)claim \n(4)claimToClaimType \n(5)claimToClaim \n(6)replyText \n(7)replyToClaimType \n(8)replyToClaim \n(9)replyToReplyType \n(10)replyToReply\n? "))
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
        print("\n")
        print("Invalid input. Try again.")
        continue

    results = cursor.execute("select * from " + table)
    print("\n")
    for row in results:
        print(row)
    print("\n")

db.close()
