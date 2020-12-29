import socket, struct
from enum import IntEnum
from threading import Thread
from time import sleep
import sys

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

def GetData(ID):
    while True:
        clientSock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connect(clientSock)
        SendMessage(clientSock, ID, 0, MessageTypes.M_GETDATA)
        msg=Message()
        if (msg.ReceiveData(clientSock)==MessageTypes.M_TEXT):
            print('Message from client '+str(msg.m_Header.m_From)+': '+msg.m_Data.decode('utf-8'))
        disconnect(clientSock)
        sleep(1)

MyID=0
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    connect(s)
    SendMessage(s, 0, 0, MessageTypes.M_INIT)
    msg=Message()
    if (msg.ReceiveData(s)==MessageTypes.M_CONFIRM):
        MyID=msg.m_Header.m_To
        print('Connected, My ID is '+str(MyID))
        t=Thread(target=GetData, args=(MyID,), daemon=True)
        t.start()      
        disconnect(s)
    else:
        print('Error')
        sys.exit()
while True:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        choice=int(input('1. Send Message\n2. Exit\n'))
        if choice==1:
            ClientID=Addresses.A_ALL
            choice2=int(input('1. Only for one client\n2. For All Clients\n'))
            if choice2==1:
                ClientID=int(input('Enter ID of client\n'))
            str=input('Enter your Message\n')
            connect(s)
            SendMessage(s, MyID, ClientID, MessageTypes.M_TEXT, str)
            if msg.ReceiveData(s)==MessageTypes.M_CONFIRM:
                print('succes\n')
            else: print('error\n')
            disconnect(s)
        elif choice==2:
           connect(s)
           SendMessage(s,MyID, 0, MessageTypes.M_EXIT)
           if msg.ReceiveData(s)==MessageTypes.M_CONFIRM:
               print('succes\n')
           else: print('error\n')
           disconnect(s)
           sys.exit(0)
        else:
            print('Please, press 1 or 2')
        sys.exit(0)




