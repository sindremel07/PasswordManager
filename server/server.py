from flask import Flask, request, jsonify
import mysql.connector
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
import json
import os
import base64

app = Flask(__name__)

sender_email = "esquised.app@gmail.com"
verification_password = "unai pilv sugn avps"

# Generator variables
oldDbKey = ""

Chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
Numbers = "0123456789"
CodeLinkLength = 4
FirstCodeLink = ""
SecondCodeLink = ""

# Load database configuration from config.json
with open("config.json", "r") as handler:
    config = json.load(handler)
    

def get_db_connection():
    return mysql.connector.connect(
        host=config["host"],
        user=config["user"],
        password=config["password"],
        database=config["database"]
    )

# To generate a random session id for a new registered user
def generate_session_id():
    length = 128

    generating = True

    while generating:
        num_bytes = (length * 3) // 4 + 1  
        random_bytes = os.urandom(num_bytes)
        session_id = base64.urlsafe_b64encode(random_bytes).decode('utf-8').rstrip('=')
        session_id = session_id[:length]

        # To check if the databasekey is already been generated to a different account
        mydb = get_db_connection()
        cursor = mydb.cursor(dictionary=True)
        cursor.execute(f"SELECT name FROM users WHERE session_id = '{session_id}'")
        session_idTaken = cursor.fetchone()
        mydb.close()

        generating = False

    if session_idTaken:
        generating = True
    else:
        return session_id

@app.route('/update-otc', methods=['POST'])
def check_dbkey():
    data = request.json
    dbkey = data.get('databasekey')
    otc = data.get('otc')

    mydb = get_db_connection()
    cursor = mydb.cursor(dictionary=True)

    # Check dbkey credentials
    cursor.execute(f"SELECT otc FROM users WHERE databasekey = '{dbkey}'")
    databasekey = cursor.fetchone()
    mydb.close()

    if not databasekey:
        return jsonify({'status': 401, 'message': 'Invalid credentials'}), 401
    
    if otc:
        update_otc(otc, dbkey)
        return jsonify({'status': 200, 'message': 'Found DBKey in database and updated OTC!'}), 200
    elif not otc:
        return jsonify({'status': 200, 'message': 'DBKey in database!', 'inputresult': f'{databasekey}'}), 200
    

def update_otc(otc, dbkey):

    mydb = get_db_connection()
    cursor = mydb.cursor(dictionary=True)

    # Updating OTC for the current databasekey
    sql = "UPDATE users SET otc = %s WHERE databasekey = %s"
    val = (otc, dbkey)
    cursor.execute(sql, val)
    mydb.commit()
    mydb.close()

    return jsonify({'status': 200, 'message': 'Updated OTC in database!'}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    name = data.get('name')
    password = data.get('password')

    if not name or not password:
        return jsonify({'status': 400, 'message': 'Name and password required'}), 400

    # Connect to the database
    mydb = get_db_connection()
    cursor = mydb.cursor(dictionary=True)

    # Check user credentials
    cursor.execute("SELECT * FROM users WHERE name=%s AND password=%s", (name, password))
    user = cursor.fetchone()
    mydb.close()

    if not user:
        return jsonify({'status': 401, 'message': 'Invalid credentials'}), 401

    # Return status code 200 and ask for OTP
    return jsonify({'status': 200, 'message': 'OTP required'}), 200

# Generate databasekey for new users
def generate_dbkey():
    global oldDbKey, generatedKey
    lowCase = "abcdefghijklmnopqrstuvwxyz"
    upperCase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    numbers = "123456789"
    symbols = '?!#%@^=+"&*'

    generating = True

    while generating:
        if len(oldDbKey) == 26:
            generatedKey = oldDbKey

            # To check if the databasekey is already been generated to a different account
            mydb = get_db_connection()
            cursor = mydb.cursor(dictionary=True)
            cursor.execute(f"SELECT otc FROM users WHERE databasekey = '{generatedKey}'")
            databasekey = cursor.fetchone()
            mydb.close()

            if databasekey:
                oldDbKey = ""
            elif not databasekey:
                generating = False
                oldDbKey = ""
                return generatedKey
        else:
            number = random.randint(0,3)

            if number == 0:
                oldDbKey += lowCase[random.randint(0, len(lowCase) - 1)]
            if number == 1:
                oldDbKey += upperCase[random.randint(0, len(upperCase) - 1)]
            if number == 2:
                oldDbKey += numbers[random.randint(0, len(numbers) - 1)]
            if number == 3:
                oldDbKey += symbols[random.randint(0, len(symbols) - 1)]
                
# Generate otc for the given databasekey
def generate_otc():
    global FirstCodeLink, SecondCodeLink, CompleteCode
    generating = True

    while generating:    
        if len(FirstCodeLink) == CodeLinkLength and len(SecondCodeLink) == CodeLinkLength:
            CompleteCode = f"{FirstCodeLink}-{SecondCodeLink}"
            generating = False
            FirstCodeLink = ""
            SecondCodeLink = ""
            return CompleteCode
        else:
            result = random.randint(0, 1)
            if len(FirstCodeLink) < CodeLinkLength:
                if result == 0:
                    FirstCodeLink += Chars[random.randint(0, len(Chars) - 1)]
                else:
                    FirstCodeLink += Numbers[random.randint(0, len(Numbers) - 1)]
            elif len(SecondCodeLink) < CodeLinkLength:
                if result == 0:
                    SecondCodeLink += Chars[random.randint(0, len(Chars) - 1)]
                else:
                    SecondCodeLink += Numbers[random.randint(0, len(Numbers) - 1)]



@app.route('/register-user', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')
    password = data.get('password')
    email = data.get('email')
    dbkey = generate_dbkey()
    otc = generate_otc()
    verification_key = generate_otc()
    session_id = generate_session_id()

    # To check if name is already in the database
    mydb = get_db_connection()
    cursor = mydb.cursor(dictionary=True)
    cursor.execute(f"SELECT otc FROM users WHERE name = '{name}'")
    nameTaken = cursor.fetchone()
    cursor.execute(f"SELECT name FROM users WHERE email = '{email}'")
    emailTaken = cursor.fetchone()
    mydb.close()

    if not name or not password or not email:
        return jsonify({'status': 400, 'message': 'All fields required!'}), 400
    if nameTaken:
        return jsonify({'status': 401, 'message': 'Name is already been used!'}), 401
    if emailTaken:
        return jsonify({'status': 401, 'message': 'Email is already been used!'}), 401
    else:

        sql = "INSERT INTO users (name, password, email, otc, databasekey, session_id, verification_key) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        val = (f"{name}", f"{password}", f"{email}", f"{otc}", f"{dbkey}", f"{session_id}", f"{verification_key}")

        print(f"Name: {name} | Password: {password} | Email: {email} | OTC: {otc} | DBKey: {dbkey} | VerificationKey: {verification_key}")

        subject = "Verify Your Account"
        body = f"Hello {name}, here is your verification key: {verification_key}"
        receiver_email = f"{email}"

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()  

            server.login(sender_email, verification_password)

            server.sendmail(sender_email, receiver_email, msg.as_string())

            print("Email sent successfully!")

            # Register the new user into the database
            mydb = get_db_connection()
            cursor = mydb.cursor(dictionary=True)
            cursor.execute(sql, val)

            # Create a new database for the current user where the password/info the user want's to store in the passmanager
            cursor.execute(f"CREATE TABLE {name}Database (id INT AUTO_INCREMENT PRIMARY KEY, title VARCHAR(255), name VARCHAR(255), password VARCHAR(255), email VARCHAR(255), description VARCHAR(255), website VARCHAR(255))")

            mydb.commit()
            mydb.close()
        
            return jsonify({'status': 200, 'message': 'Check inbox for verification key to activate account!'}), 200

        except Exception as e:
            print(f"Failed to send verification key to email. Error: {e}")

        finally:
            server.quit()
    
@app.route('/verify-account', methods=['POST'])
def verify_account():
    data = request.json
    email = data.get('email')
    verification_key = data.get('verification_key')

    mydb = get_db_connection()
    cursor = mydb.cursor(dictionary=True)

    cursor.execute("SELECT databasekey FROM users WHERE verification_key=%s", (verification_key,))
    fetched_databasekey = cursor.fetchone()
    mydb.close()

    print(verification_key)
    print(fetched_databasekey)

    databasekey = fetched_databasekey['databasekey']

    if databasekey == None:
        return jsonify({'status': 400, 'message': 'Wrong verification key!'}), 400
    else:
        cursor.execute("UPDATE users SET verification_key=%s verified=%s WHERE email=%s", ("", "1",email)) # 0=not verified & 1=verified

        return jsonify({'status': 200, 'message': 'Verification complete!', 'databasekey': f'{databasekey}'}), 200
    
@app.route('/get-username', methods=['POST'])
def get_username():
    data = request.json
    session_id = data.get('session_id')

    mydb = get_db_connection()
    cursor = mydb.cursor(dictionary=True)

    # Fetch user OTP from the database
    cursor.execute("SELECT name FROM users WHERE session_id=%s", (session_id,))
    fetched_name = cursor.fetchone()
    mydb.close()

    name = fetched_name['name']

    return jsonify({'name': f'{name}'})

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.json
    name = data.get('name')
    otp = data.get('otp')

    if not name or not otp:
        return jsonify({'status': 400, 'message': 'Name and OTP required'}), 400

    # Connect to the database
    mydb = get_db_connection()
    cursor = mydb.cursor(dictionary=True)

    # Fetch user OTP from the database
    cursor.execute("SELECT otc FROM users WHERE name=%s", (name,))
    user = cursor.fetchone()
    cursor.execute("SELECT session_id FROM users WHERE name=%s", (name,))
    fetched_session_id = cursor.fetchone()
    mydb.close()

    if user:
        stored_otp = user['otc']
        session_id = fetched_session_id['session_id']
        print(f"Received OTP: {otp}")  # Debugging statement
        print(f"Stored OTP: {stored_otp}")  # Debugging statement

        if otp == stored_otp:
            # Optionally, update or invalidate the OTP here if needed

            return jsonify({'status': 200, 'session_id': f'{session_id}'}), 200
        else:
            return jsonify({'status': 401, 'message': 'Invalid OTP'}), 401
    else:
        return jsonify({'status': 401, 'message': 'User not found'}), 401
    
# Info Database Add, Remove, Update functions

@app.route('/addto-infodb', methods=['POST'])
def addto():
    data = request.json
    session_id = data['session_id']
    infotitle = data['infotitle']
    infoname = data['infoname']
    infomail  = data['infomail']
    infopass = data['infopass']
    infodesc = data['infodesc']
    website = data['website']

    mydb = get_db_connection()
    cursor = mydb.cursor(dictionary=True)

    # Fetch name from database with session_id
    cursor.execute("SELECT name FROM users WHERE session_id=%s", (session_id,))
    fetched_name = cursor.fetchone()
    mydb.close()

    name = fetched_name['name']

    if not session_id or not infotitle or not infoname or not infopass or not infodesc:
        return jsonify({'status': 400, 'message': 'All fields required!'}), 400
    if not name:
        return jsonify({'status': 400, 'message': 'Invalid credentials!'}), 401
    
    # Connect to the database
    mydb = get_db_connection()
    cursor = mydb.cursor(dictionary=True)

    sql = f"INSERT INTO {name}database (title, name, password, email, description, website) VALUES (%s, %s, %s, %s, %s, %s)"
    val = (f"{infotitle}", f"{infoname}", f"{infopass}", f"{infomail}", f"{infodesc}", f"{website}")
    cursor.execute(sql, val)
    
    mydb.commit()
    mydb.close()

    return jsonify({'status': 200, 'message': 'Success!'}), 200

@app.route('/removefrom-infodb', methods=['POST'])
def removefrom():
    data = request.json
    session_id = data['session_id']
    id = data['id']

    mydb = get_db_connection()
    cursor = mydb.cursor(dictionary=True)

    # Fetch name from database with session_id
    cursor.execute("SELECT name FROM users WHERE session_id=%s", (session_id,))
    fetched_name = cursor.fetchone()

    name = fetched_name['name']

    cursor.execute(f"SELECT * FROM {name}database WHERE id = %s", (id,))
    fetched_id = cursor.fetchone()
    mydb.close()

    if not session_id or not id:
        return jsonify({'status': 400, 'message': 'All fields required!'}), 400
    if not name:
        return jsonify({'status': 400, 'message': 'Invalid credentials!'}), 401
    if not fetched_id:
        return jsonify({'status': 400, 'message': 'Could not delete row!'}), 400


    # Connect to the database
    mydb = get_db_connection()
    cursor = mydb.cursor(dictionary=True)

    sql = f"DELETE FROM {name}database WHERE id = %s"
    val = (f"{id}",)
    cursor.execute(sql, val)
    
    mydb.commit()
    mydb.close()

    return jsonify({'status': 200, 'message': 'Success!'}), 200


@app.route('/getdata-infodb', methods=['POST'])
def getdata():
    data = request.json
    session_id = data['session_id']


    if not session_id:
        return jsonify({'status': 400, 'message': 'Could not retrieve data.'}), 400
    
    mydb = get_db_connection()
    cursor = mydb.cursor(dictionary=True)

    # Fetch name from database with session_id
    cursor.execute("SELECT name FROM users WHERE session_id=%s", (session_id,))
    fetched_name = cursor.fetchone()

    name = fetched_name['name']

    cursor.execute(f"SELECT * FROM {name}database")
    fetched_data = cursor.fetchall()
    mydb.close()

    return jsonify({'status': 200, 'data': f'{fetched_data}'})

@app.route('/update-infodb', methods=['POST'])
def update_data():
    data = request.json
    title = data.get('title')
    id = data.get('id')
    session_id = data.get('session_id')

    mydb = get_db_connection()
    cursor = mydb.cursor(dictionary=True)

    # Fetch name from the database using session_id
    cursor.execute("SELECT name FROM users WHERE session_id = %s", (session_id,))
    fetched_name = cursor.fetchone()

    if not fetched_name:
        return jsonify({'status': 400, 'message': 'Invalid session ID.'}), 400

    name = fetched_name['name']

    # If title is provided, update title in the database
    if title:
        sql = f"UPDATE `{name}database` SET title = %s WHERE id = %s"
        cursor.execute(sql, (title, id))
        mydb.commit()
        return jsonify({'status': 200, 'message': 'Title updated successfully!'})

    # Get other fields from the request data
    infoname = data.get('name')
    password = data.get('password')
    email = data.get('email')
    description = data.get('description')
    website = data.get('website')

    # Validate required fields
    if not infoname and not password and not email and not description and not website:
        return jsonify({'status': 400, 'message': 'At least one field must be filled.'}), 400
    if not infoname or not password:
        return jsonify({'status': 400, 'message': 'Name and password are required.'}), 400

    # Update the database with the provided fields
    sql = f"""
        UPDATE `{name}database`
        SET name = %s, password = %s, email = %s, description = %s, website = %s
        WHERE id = %s
    """
    cursor.execute(sql, (infoname, password, email, description, website, id))
    mydb.commit()

    return jsonify({'status': 200, 'message': 'Data updated successfully!'})



if __name__ == '__main__':
    app.run(ssl_context=('cert.pem', 'key.pem'))
