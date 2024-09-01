import json
import time
import random
from tkinter import *
from tkinter import ttk
import requests

root = Tk()
root.title('Authenticator App')
root.geometry("500x400")
root.resizable(0,0)

startTime = time.time()
timerTime = 34
# Open json files
with open("databasekeys.json", "r") as handler:
    keys = json.load(handler)

with open("config.json", "r") as handler:
    config = json.load(handler)

def newdbkey():
    with open("databasekeys.json", "r") as handler:
        return json.load(handler)

# Code generator variables
x = 0
number = 0

databasekeyList = []
namelist = []
OTCLabelList = []
CodeFrameList = []

UPDATE_OTP_URL = 'http://localhost:5000/update-otc'


Chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
Numbers = "0123456789"
CodeLinkLength = 4
FirstCodeLink = ""
SecondCodeLink = ""


for key in keys:
    databasekeyList.append(keys[x]['Key'])
    namelist.append(keys[x]['Name'])
    x = x + 1

# Images
showImg = PhotoImage(file = "images/show.png")
hideImg = PhotoImage(file = "images/hide.png")

dbinputvar=StringVar()
nameinputvar=StringVar()

isShowing = False

def generate():
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


def show():
    global isShowing, showbtn, dbinput_label, dbinput_entry, sub_btn, nameinput_label, nameinput_entry, newotcframe

    if isShowing:
        isShowing = False
        showbtn.config(image=showImg)
        nameinput_label.place_forget()
        nameinput_entry.place_forget()
        dbinput_label.place_forget()
        dbinput_entry.place_forget()
        sub_btn.place_forget()
        error_label.place_forget()
        newotcframe.place_forget()
    else:
        isShowing = True
        showbtn.config(image=hideImg)
        nameinput_label.place(x=10, y=10)
        nameinput_entry.place(x=13, y=30)
        dbinput_label.place(x=10, y=50)
        dbinput_entry.place(x=13, y=70)
        sub_btn.place(x=13, y=170)
        newotcframe.place(x=135, y=150)


def submit():
    global namelist, databasekeyList, error_label, input_entry, addDb, sub_btn, nameinput_entry, nameinput_label, number
    
    name=nameinputvar.get()
    dbkey=dbinputvar.get()

    response = requests.post(UPDATE_OTP_URL, json={'databasekey': dbkey}, verify=False)
    if response.status_code == 200:
        inputresult = response.json().get('inputresult')

    if len(dbkey) != 26 or inputresult == None:
        if len(databasekeyList) < 1:
            error_label.place(x=205, y=90)
            error_label.config(fg="red", text="Invalid Key!")
        else:  
            error_label.place(x=282, y=378)
            error_label.config(fg="red", text="Invalid Key!")
    elif dbkey in databasekeyList:
        error_label.place(x=270, y=378)
        error_label.config(fg="red", text="Key Already Added!")
    else:
        if len(databasekeyList) < 1:
            error_label.place(x=215, y=90)
            error_label.config(fg="green", text="Success")
            error_label.place_forget()
            input_entry.place_forget()
            addDb.place_forget()
            nameinput_entry.place_forget()
            nameinput_label.place_forget()
            sub_btn.place_forget()

            data = []
            dbKeyData = {
                "Name": name,
                "Key": dbkey
            }
            data.append(dbKeyData)

            with open("databasekeys.json", "w") as file:
                json.dump(data, file, indent=4)

            databasekeyList.append(dbkey)
            namelist.append(name)
            main()
        else:
            error_label.place(x=290, y=378)
            error_label.config(fg="green", text="Success")

            data = []
            dbKeyData = {
                "Name": name,
                "Key": dbkey
            }
            data.append(dbKeyData)

            oldDbKeys = newdbkey()

            with open("databasekeys.json", "w") as file:
                json.dump(oldDbKeys + data, file, indent=4)

            databasekeyList.append(dbkey)
            namelist.append(name)
            
            OTC = generate() #7uMv8zm?gNal+bjNClrjCq%d#7

            requests.post(UPDATE_OTP_URL, json={'databasekey': dbkey, 'otc': OTC}, verify=False)

            SecondFrame = Frame(MainFrame, width=300, height=50)
            SecondFrame.pack(pady=5)

            CodeFrame = Frame(SecondFrame, width=300, height=55, cursor="hand2")
            CodeFrame.pack(pady=0)

            BottomBorder = Frame(SecondFrame, bg="#bec1c0", height=1, width=300)
            BottomBorder.pack(side=BOTTOM, fill=X)

            name_label = Label(CodeFrame, text=f"Account: {namelist[number]}", font=("Helvetica", 8, "bold"))
            name_label.grid(row=0, column=0, sticky=W)

            code_label = Label(CodeFrame, text=f"{OTC}", font=("Helvetica", 18))
            code_label.grid(row=1, column=0, sticky=W)

            number += 1

            CodeFrame.bind("<Button-1>", lambda event, otc=OTC: copy_to_clipboard(otc))

            CodeFrame.grid_propagate(False)
            OTCLabelList.append(code_label)
            CodeFrameList.append(CodeFrame)


    dbinputvar.set("")
    nameinputvar.set("")

def update_timer():
    global startTime, timerTime

    currentTime = round(time.time() - startTime)
    timerTime = 34 - currentTime

    timer_label.config(text=f"New Code in {timerTime} Seconds")
    
    if currentTime >= 34:
        startTime = time.time()
        timerTime = 34
        update_ui()
    else:
        root.after(1000, update_timer) 

def update_ui():
    for i, dbKey in enumerate(databasekeyList):
        OTC = generate()  

        requests.post(UPDATE_OTP_URL, json={'databasekey': dbKey, 'otc': OTC}, verify=False)

        OTCLabelList[i].config(text=f"{OTC}")  
        CodeFrameList[i].bind("<Button-1>", lambda event, otc=OTC: copy_to_clipboard(otc))
    
    update_timer()

def copy_to_clipboard(OTC):
    root.clipboard_clear()  
    root.clipboard_append(OTC)  
    root.update()  
    print("Copied", f"OTC code {OTC} copied to clipboard!")

def main():   
    global error_label, sub_btn, input_entry, addDb, nameinput_label, nameinput_entry, dbinput_label, dbinput_entry, code_label
    global timer_label, showbtn, timerTime, startTime, OTCLabelList, newotcframe, number, MainFrame, CodeFrameList
    if len(databasekeyList) == 0:
        nameinput_label = Label(root, text="Account Name", font=("Helvetica", 16))
        nameinput_label.place(x=185, y=20)

        nameinput_entry = Entry(root, textvariable=nameinputvar, font=("Helvetica", 16))
        nameinput_entry.place(x=132, y=55)

        addDb = Label(root, text="DatabaseKey", font=("Helvetica", 16))
        addDb.place(x=185, y=95)

        input_entry = Entry(root, textvariable=dbinputvar, font=("Helvetica", 16))
        input_entry.place(x=132, y=125)

        sub_btn=Button(root,text = 'Add', command = submit, font=("Helvetica", 12), width=25)
        sub_btn.place(x=135, y=165)

        error_label = Label(root, font=("Helvetica", 12))
    else:
        timer_label = Label(root, text=f"New Code in {timerTime} Seconds", font=("Helvetica", 14))
        timer_label.pack(pady=0)

        MainFrame = Frame(root, width=300, height=500)
        MainFrame.pack(pady=5)

        TopBorder = Frame(MainFrame, bg="#bec1c0", height=1, width=300)
        TopBorder.pack(side=TOP, fill=X)

        for dbKey in databasekeyList:
            OTC = generate() 

            requests.post(UPDATE_OTP_URL, json={'databasekey': dbKey, 'otc': OTC}, verify=False)

            SecondFrame = Frame(MainFrame, width=300, height=50)
            SecondFrame.pack(pady=5)

            CodeFrame = Frame(SecondFrame, width=300, height=55, cursor="hand2")
            CodeFrame.pack(pady=0)

            BottomBorder = Frame(SecondFrame, bg="#bec1c0", height=1, width=300)
            BottomBorder.pack(side=BOTTOM, fill=X)

            name_label = Label(CodeFrame, text=f"Account: {namelist[number]}", font=("Helvetica", 8, "bold"))
            name_label.grid(row=0, column=0, sticky=W)

            code_label = Label(CodeFrame, text=f"{OTC}", font=("Helvetica", 18))
            code_label.grid(row=1, column=0, sticky=W)

            number += 1
            
            CodeFrame.bind("<Button-1>", lambda event, otc=OTC: copy_to_clipboard(otc))

            CodeFrame.grid_propagate(False)
            OTCLabelList.append(code_label)
            CodeFrameList.append(CodeFrame)

      

        newotcframe = Frame(root, width=210, height=200, bg="#d8dad9")

        nameinput_label = Label(newotcframe, bg="#d8dad9", text="Account Name", font=("Helvetica", 10))

        nameinput_entry = Entry(newotcframe, bg="#d8dad9", textvariable=nameinputvar, font=("Helvetica", 10), width=25)

        dbinput_label = Label(newotcframe, bg="#d8dad9", text="DatabaseKey", font=("Helvetica", 10))

        dbinput_entry = Entry(newotcframe, bg="#d8dad9", textvariable=dbinputvar, font=("Helvetica", 10), width=25)

        error_label = Label(newotcframe, bg="#d8dad9", font=("Helvetica", 7))   

        sub_btn=Button(newotcframe,text = 'Add', width=24, command=submit)

        

        showbtn=Button(root,image=showImg, cursor="hand2", border=0, command = show, font=("Helvetica", 24))
        showbtn.place(x=440, y=340)
        
        update_timer()

main()
root.mainloop()