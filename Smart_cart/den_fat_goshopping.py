import pyodbc
print("out here")
dsn = 'rpitestsqlserverdatasource'
user = 'deng-fat@deng-fat-goshopping'
password = 'TJG1ul3au4a83'
database = 'Shopping_Mall_Example'
connString = 'DSN={0};UID={1};PWD={2};DATABASE={3};'.format(dsn,user,password,database)
conn = pyodbc.connect(connString)
cursor = conn.cursor()
cursor.execute("UPDATE ITEM SET Remainings = Remainings + 1 WHERE(Item_Name = 'apple');")
cursor.execute("SELECT * FROM Item WHERE(Remainings > 0);")

row = cursor.fetchone()
while row:
    print(row)
    row = cursor.fetchone()
conn.commit()
