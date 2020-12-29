import socket, struct
from enum import IntEnum

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