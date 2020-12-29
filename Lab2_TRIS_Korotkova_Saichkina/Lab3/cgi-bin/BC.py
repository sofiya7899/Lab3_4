import socket, struct
from enum import IntEnum
from threading import Thread
from time import sleep
import sys
import pickle, cgitb, codecs, datetime
import cgi
import os
import html


form = cgi.FieldStorage()
action = form.getfirst("action", "")

HOST = '127.0.0.1'
PORT = 12345

class Addresses(IntEnum):
    A_BROCKER = 0
    A_ALL = -1

class MessageTypes(IntEnum):
    M_INIT=0
    M_EXIT=1
    M_CONFIRM=2
    M_GETDATA=3
    M_TEXT=4
    M_NODATA=5

class MsgHeader():
    def __init__(self, m_From=0, m_To=0, m_Type=0, m_Size=0):
        self.m_From=m_From
        self.m_To=m_To
        self.m_Type=m_Type
        self.m_Size=m_Size
    def HeaderInit(self, header):
        self.m_From=header[0]
        self.m_To=header[1]
        self.m_Type=header[2]
        self.m_Size=header[3]


class Message():
    def __init__(self, From=0, To=0, Type=MessageTypes.M_TEXT, Data=''):
        self.m_Header=MsgHeader()
        self.m_Header.m_From=From;
        self.m_Header.m_To=To;
        self.m_Header.m_Type=Type;
        self.m_Header.m_Size=int(len(Data))
        self.m_Data=Data
    def SendData(self, s):
        s.send(struct.pack('i', self.m_Header.m_From))
        s.send(struct.pack('i', self.m_Header.m_To))
        s.send(struct.pack('i', self.m_Header.m_Type))
        s.send(struct.pack('i', self.m_Header.m_Size))
        if self.m_Header.m_Size>0:
            s.send(struct.pack(f'{self.m_Header.m_Size}s', self.m_Data.encode('utf-8')))
    def ReceiveData(self, s):
        self.m_Header=MsgHeader()
        self.m_Header.HeaderInit(struct.unpack('iiii', s.recv(16)))
        if self.m_Header.m_Size>0:
            self.m_Data=struct.unpack(f'{self.m_Header.m_Size}s', s.recv(self.m_Header.m_Size))[0]
        return self.m_Header.m_Type
def SendMessage(Socket, From, To, Type=MessageTypes.M_TEXT, Data=''):
    m=Message(From, To, Type, Data)
    m.SendData(Socket)
def Receive(Socket):
    m=Message()
    res=m.ReceiveData(Socket)
    return res
def connect(Socket):
    Socket.connect((HOST, PORT))

def disconnect(Socket):
    Socket.close()

#ГЛОБАЛЬНЫЕ ПЕРМЕННЫЕ
global MYID
MYID=0

DB = 'messages.db'

global MESSAGES
MESSAGES={"messages": []}



systemMessage=""


def load():
    with open(DB, 'rb') as f:
        (MYID, MESSAGES) = pickle.load(f)
    
def store():
    with open(DB, 'wb') as f:
        pickle.dump((MYID, MESSAGES), f)
        
        
def AddMessage(To, From, Data):
        load()
        MESSAGES["messages"].append({'From': int(From), 'To': int(To), 'Data': Data})
        store()

def GetMessages():
        load()
        posts=[]
        for post in MESSAGES["messages"]:
            content='Message from '+str(post['From'])+' to client '+str(post['To'])+': '+post['Data']
            posts.append(content)
        return '<br>'.join(posts)

#HTML формы   
InitForm='''
<form action="/cgi-bin/BC.py">
    <input type="hidden" name="action" value="Init">
    <input type="submit" value="Init To Server">
</form>
'''



#Вся страница  
htmlPage='''
<!DOCTYPE HTML>
<html>
<head>
<meta charset="utf-8">
<title>Lab3</title>
</head>
<body>
    {init}
    {messages}
    {send}
	<br>
	{getdata}
    <br>
    {system}
</body>
</html>
'''

#НАЧАЛО РАБОТЫ ПРОГРАММЫ
try:
    with open(DB, 'rb') as f:
        (MYID, MESSAGES) = pickle.load(f)
    
except:
    store()


if action=="Init":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        connect(s)
        SendMessage(s, MYID, 0, MessageTypes.M_INIT)
        msg=Message()
        if (msg.ReceiveData(s)==MessageTypes.M_CONFIRM):
            if (MYID==0):
                MYID=msg.m_Header.m_To
                store()
            systemMessage='Connected, My ID is '+str(MYID)
        else:
            systemMessage="Something went wrong"
        disconnect(s)

if MYID!=0:
    SendForm='''
    <form action="/cgi-bin/BC.py">
        <input type="text" name="m_To">
        <textarea name="m_Data"></textarea>
        <input type="hidden" name="action" value="Send">
        <input type="submit" value="Send Message">
    </form>
    '''
    GetMessForm='''
    <form action="/cgi-bin/BC.py">
        <input type="hidden" name="action" value="GetData"> 
        <input type="submit" value="Get Data">
    </form>    
    '''
else:
    SendForm=''
    GetMessForm=''


if action=="Send":
    m_To=form.getfirst("m_To", "")
    m_To=html.escape(m_To)
    m_Data = form.getfirst("m_Data", "")
    m_Data = html.escape(m_Data)
    if m_Data is not None:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                connect(s)
                SendMessage(s, MYID, int(m_To), MessageTypes.M_TEXT, m_Data)
                msg=Message()
                if msg.ReceiveData(s)==MessageTypes.M_CONFIRM:
                    systemMessage='succes'
                else: systemMessage='error'
                disconnect(s)
        except:
            systemMessage="Something went wrong, try to Init again "

if action=="GetData":
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            connect(s)
            SendMessage(s, MYID, 0, MessageTypes.M_GETDATA)
            msg=Message()
            if (msg.ReceiveData(s)==MessageTypes.M_TEXT):
                AddMessage(msg.m_Header.m_To, msg.m_Header.m_From, msg.m_Data.decode('utf-8'))
                
            disconnect(s)
    except:
        systemMessage="Something went wrong, try to Init again "

print('Content-type: text/html\n')

if MYID!=0:
    print('USER ID: ', MYID, '<br>')
else:
    print('Press Init To Connect', '<br>')

print(htmlPage.format(init=InitForm, messages=GetMessages(), send=SendForm, getdata=GetMessForm, system=systemMessage))