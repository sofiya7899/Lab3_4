from messageClass import *

from threading import Thread
from time import sleep
import sys
import pickle, cgitb, codecs, datetime
import cgi
import os
import html
import json

from urllib.parse import parse_qs

#Для разного типа подключения (рест или веб) разный тип отправляемых данных
htmlContent='Content-type: text/html\n'
jsonContent='Content-type: application/json\n'


#В Этом блоке принимается запрос и данные 
content_len = os.environ.get('CONTENT_LENGTH', '0')#длина отправляемых данных
method = os.environ.get('REQUEST_METHOD', '')#метод (Пост или Гет)
query_string = os.environ.get('QUERY_STRING', '') #ссылка запроса (в ссылке запроса могут содержаться данные)
if (content_len!=''): #Если мы из какого то клиента отправили данные (методом пост), то ...
    body = sys.stdin.read(int(content_len)) #Записываем эти данные в переменную body
else:
    body=query_string #если не отправляли данные, то записываем ссылку запроса (то, что идет после localhost/..../BC.py?)




#ГЛОБАЛЬНЫЕ ПЕРМЕННЫЕ
MYID=0
DB = 'messages.db'
MESSAGES={"messages": []}
action='' #действие (Init, GetData, Send)
BCData=''#данные принимаемые от браузера
RCData={} #данные, принимаемые от реста (формат json)
toRestData={#данные, отправляемые ресту
    'id_To':0,
    'id_From':0,
    'Data':'',
    'system':''
}
systemMessage=""#Системное сообщение (ответ от сервера из первой лабы)
restFlag=False;#Флаг переключатель режима работы (если false - работаем с браузером)


#В этом блоке присваиваем переменной action то действие, которое пришло от Браузера
#Или от реста. Еще присваиваем переменной RCData/BCData отправленные от рест/браузера данные
if (query_string.find('console=1')!=-1):
    if(query_string.find('action=GetData')!=-1):
        action='GetData'
    else:
        RCData=json.loads(body)
        action=RCData['action']
    restFlag=True
else:
    BCData=parse_qs(body)
    try:
        action=BCData['action'][0]
    except:
        pass


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
<form method="post"  action="/cgi-bin/BC.py">
    <input type="hidden" name="action" value="Init">
    <input type="submit" value="Init To Server">
</form>
'''


SendForm='''
<form method="post" action="/cgi-bin/BC.py">
    <input type="text" name="m_To">
    <textarea name="m_Data"></textarea>
    <input type="hidden" name="action" value="Send">
    <input type="submit" value="Send Message">
</form>
'''
GetMessForm='''
<form method="get" action="/cgi-bin/BC.py">
    <input type="hidden" name="action" value="GetData"> 
    <input type="submit" value="Get Data">
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
        toRestData['id_To']=MYID




if action=="Send":
    m_To=None
    m_Data=None

    if restFlag==True:
        try:
            m_To=RCData['m_To']
            m_Data=RCData['m_Data']
        except:
            pass
    else:
        try:
            m_To=BCData['m_To'][0]
            m_Data=BCData['m_Data'][0]
        except:
            pass

    if m_Data is not None and m_To is not None:
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
                
                toRestData['id_From']=int(msg.m_Header.m_From)
                toRestData['Data']=str(msg.m_Data)
            disconnect(s)
    except:
        systemMessage="Something went wrong, try to Init again "

toRestData['system']=systemMessage

if restFlag==True:
    print(jsonContent)
    print(json.dumps(toRestData))
else:
    print(htmlContent)

    if MYID!=0:
        print('USER ID: ', MYID, '<br>')
    else:
        print('Press Init To Connect', '<br>')
        SendForm=''
        GetMessForm=''

    print(htmlPage.format(init=InitForm, messages=GetMessages(), send=SendForm, getdata=GetMessForm, system=systemMessage))