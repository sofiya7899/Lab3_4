// Client_C++.cpp : Этот файл содержит функцию "main". Здесь начинается и заканчивается выполнение программы.
//

#include "pch.h"
#include "framework.h"
#include "Client_C++.h"


#include <iostream>
#include <afxsock.h>
#include <queue>
#include <map>
#include <thread>
#include <mutex>
#include <string>

#include "Message.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#endif


// Единственный объект приложения

CWinApp theApp;

using namespace std;

int MyID;

void connect(CSocket& S) {
    S.Create();
    S.Connect(_T("127.0.0.1"), 12345);
}

void disconnect(CSocket& S) {
    S.Close();
}

void GetData() {
    while (true) {
        CSocket s;
        connect(s);
        Message m;
        Message::SendMessage(s, A_BROCKER, MyID, M_GETDATA);
        if (m.Receive(s) == M_TEXT) {
            cout << "Message from " << m.getHeader().m_From << ": " << m.getData() << endl;
        }
        disconnect(s);
        Sleep(1000);
    }
}

void Client() {
    //ИНИЦИАЛИЗАЦИЯ СОКЕТОВ И ПОДКЛЮЧЕНИЕ К СЕРВЕРУ
    AfxSocketInit();
    CSocket client;
    connect(client);
    Message::SendMessage(client, 0, 0, M_INIT);
    Message m;
    if (m.Receive(client) == M_CONFIRM) {
        MyID = m.getHeader().m_To;
        cout << "My id is " << MyID << endl;
        thread t(GetData);
        t.detach();
    }
    else {
        cout << "error" << endl;
        return;
    }
    disconnect(client);

    //ПЕРЕДАЧА И ПРИЕМ СООБЩЕНИЙ
    while (true) {
        cout << "1. Send Message\n2. Exit\n";
        int choice;
        cin >> choice;

        switch (choice) {
        case 1: {
            int ClientID=A_ALL;
            cout << "1. Only for one client\n2. For All Clients\n";
            int choice2;
            cin >> choice2;
            if (choice2 == 1) {
                cout << "Enter ID of client\n";
                cin >> ClientID;
            }
            

            cout << "Enter your Message\n";
            string str;
            cin.ignore();
            getline(cin, str);
            connect(client);
            Message::SendMessage(client, ClientID, MyID, M_TEXT, str);
            if (m.Receive(client) == M_CONFIRM) {
                cout << "succes\n";
            }
            else {
                cout << "error\n";
            }
            disconnect(client);

            break;
        }

        case 2: {
            connect(client);
            Message::SendMessage(client, A_BROCKER, MyID, M_EXIT);
            if (m.Receive(client) == M_CONFIRM) {
                cout << "succes\n";
            }
            else {
                cout << "error\n";
            }
            disconnect(client);
            return;
        }
        default:
            break;
        }
    }

}

int main()
{
    int nRetCode = 0;

    HMODULE hModule = ::GetModuleHandle(nullptr);

    if (hModule != nullptr)
    {
        // инициализировать MFC, а также печать и сообщения об ошибках про сбое
        if (!AfxWinInit(hModule, nullptr, ::GetCommandLine(), 0))
        {
            // TODO: вставьте сюда код для приложения.
            wprintf(L"Критическая ошибка: сбой при инициализации MFC\n");
            nRetCode = 1;
        }
        else
        {
            // TODO: вставьте сюда код для приложения.
            Client();
        }
    }
    else
    {
        // TODO: измените код ошибки в соответствии с потребностями
        wprintf(L"Критическая ошибка: сбой GetModuleHandle\n");
        nRetCode = 1;
    }

    return nRetCode;
}
