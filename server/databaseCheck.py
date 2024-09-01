import mysql.connector
import json
from cryptography.fernet import Fernet
from mysql.connector import errorcode


key = Fernet.generate_key()
f = Fernet(key)
print(key)
token = f.encrypt(b"my deep dark secret")
token
b'...'
f.decrypt(token)
b'my deep dark secret'

with open("config.json", "r") as handler:
    config = json.load(handler)

mydb = mysql.connector.connect(
  host=config["host"],
  user=config["user"],
  password=config["password"],
  database=config["database"]
)

mycursor = mydb.cursor()

# mycursor.execute("CREATE DATABASE PasswordManagerDatabase")
mycursor.execute(f"""
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY, 
    name VARCHAR(255), 
    password VARCHAR(255), 
    email VARCHAR(255), 
    otc VARCHAR(255), 
    databasekey VARCHAR(255),
    session_id VARCHAR(255),
    verification_key VARCHAR(255),
    verified VARCHAR(20) DEFAULT '0',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP             
)""")

tables_to_delete = [
    "accdatabase",
    "asasasasasdatabase", "asasasdatabase", "brbrbrdatabase",
    "sdsddatabase", "test1database", "testdatabase", "testssssdatabase"
]

# mycursor.execute("DROP TABLE users")
# mycursor.execute("DROP TABLE bobdatabase")
# mycursor.execute("DROP TABLE testdatabase")
# mycursor.execute("DROP TABLE alexdatabase")

for x in tables_to_delete:
    break
    #mycursor.execute(f"DROP TABLE {x}")
    #mydb.commit()


mydb.commit()
mycursor.execute("select * from users")
a = mycursor.fetchall()

for x in a:
    print(x)