import requests
import json
import threading
import time
from threading import Lock

mutex = Lock() #мьютекс

#функция вывода в консоль какой то строки
def PrintMess(text):
	mutex.acquire()
	print(text)
	mutex.release()

#функция отправки запроса веб серверу (который в своб очередь взаимодействует с Chat.py по ссылке)
def DoRequest(method, cmd="", data=""):
    try:
        url = 'http://localhost:8080/cgi-bin/BC.py?console=1' #Пишем ссылку, что мы работаем через рест клиент 
        #(указываем нужный модуль - Chat.py  указываем console=1 чтобы Chat.py понимал о рест клиенте)


        header = {'Content-type': 'application/json'} #Говорим, что обмениваемся json данными
        res = method(url + cmd, headers=header, data=json.dumps(data))#отправляем запрос
        if res.status_code == 200: #Если успешно получили ответ 200 (т.е. успех), то возвращаем ответ от сервера
            #print(res.content)
            return res.json()
            
    except Exception as ex:
        print(ex)

#трансформирует наши данные в ссылку (используется при get, так как при get никаких данных мы не отправляем)
#И запрос формируется чисто по ссылке
def TransformToCmd(query_params):
	cmd='&'
	i=0
	for [key, value] in query_params.items():
		cmd+=key+'='+value
		i+=1
		if len(query_params.items()) !=i:
			cmd+='&'
	return cmd

#Функция подключения к локальному серверу
def Init():
	query_params={
		"action":"Init"
	}
	return DoRequest(requests.post, "", query_params) #отправляем пост запрос на подключение


def SendMess(m_To=0, m_Data=""):
	query_params={
		'm_To':m_To,
		'm_Data':m_Data,
		'action':'Send'
	}

	return DoRequest(requests.post, "", query_params) #отправляем пост запрос на передачу сообщения 

def GetData():
	query_params={
		'action':'GetData'
	}
	return DoRequest(requests.get,TransformToCmd(query_params)) #отправляем ГЕТ запрос на получения сообщения от сервера

#Прослушиваем сервер на наличие сообщений
def listenServer():
	while True:
		#SetConsole()
		m=GetData()
		if m['Data']!='':
			PrintMess('Message from client '+ str(m['id_From'])+  
				': '+ str(m['Data'])+ '\n')
		time.sleep(2)

#Подключаемся к серверу и считываем ответ 
def connect():
	m=Init()
	if m['id_To']!='':#Если мы получили наш ID, то все окей и печатаем на консоль нужно сообщение
		PrintMess(str(m['system']))
		PrintMess('Your id is '+ str(m['id_To']))
		GD_th=threading.Thread(target=listenServer, daemon=True) #Запускаем новый поток, для прослушивания сервера на наличие сообщений
		GD_th.start()

#Работа самого рес клиента, есть только возможность отправки сообщений (разрыв с сервером не реализован)
def ClientProc():
	while True:
		#SetConsole()
		print('1. Send Message\n')
		choice=int(input())

		if choice==1:
			m_to=int(input('Enter ID of client: '))
			mess=str(input('Enter your message: '))
			PrintMess(str(SendMess(m_to, mess)['system']))
		else:
			PrintMess('Error')


connect()#Сначала подключаемся к серверу
ClientProc() #Потом начинаем работать