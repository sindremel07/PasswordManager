import secrets
import string
import random

letters = string.ascii_letters
digits = string.digits
special_chars = string.punctuation

includeDigits = False
includeSymbols = False
includeLetters = True
lenght = 16

selection_list = ""


if includeDigits:
    selection_list = selection_list + digits
if includeLetters:
    selection_list = selection_list + letters
if includeSymbols:
    selection_list = selection_list + special_chars



while True:
    password = ''
    for i in range(lenght):
        password += ''.join(secrets.choice(selection_list))

    if (any(char in special_chars for char in password) and 
    sum(char in digits for char in password)>=2): 
        print(password)
        break