// Lab2_TRIS_Korotkova_Saichkina_SERVER.cpp : Этот файл содержит функцию "main". Здесь начинается и заканчивается выполнение программы.
//

#include "pch.h"
#include "framework.h"
#include "Lab2_TRIS_Korotkova_Saichkina_SERVER.h"
#include "Message.h"
#include "Session.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#endif


// Единственный объект приложения

CWinApp theApp;

int MaxID = 0;
map<int, shared_ptr<Session>> Sessions;

void TimeOut() {
    while (true)
    {
        for (auto i = Sessions.begin(); i != Sessions.end();) {
            if (Sessions.find(i->first) != Sessions.end()) {
                if (double(clock() - i->second->getTime()) > 60000) {
                    cout << "Client " << i->first << " has been disconnected" << endl;
                    i = Sessions.erase(i);
                }
                else
                    i++;
            }
        }
        Sleep(1000);
    }
}

void ProcClient(SOCKET hSOCK) {
    CSocket s;
    s.Attach(hSOCK);
    Message m;

    switch (m.Receive(s)) {
    case M_INIT: {
        int ID;
        if (m.getHeader().m_From != 0) {
            ID = m.getHeader().m_From;
        }
        else {
            MaxID++;
            ID = MaxID;
        }
        Sessions[ID] = make_shared<Session>(ID, clock());
        cout << "Client " << ID << " connect\n";
        Message::SendMessage(s, ID, A_BROCKER, M_CONFIRM); 
        break;
    }
    case M_EXIT: {
        Sessions.erase(m.getHeader().m_From);
        cout << "Client " << m.getHeader().m_From << " disconnect\n";
        Message::SendMessage(s, m.getHeader().m_From, A_BROCKER, M_CONFIRM);
        break;
    }
    case M_GETDATA: {
        if (Sessions.find(m.getHeader().m_From) != Sessions.end()) {
            Sessions[m.getHeader().m_From]->Send(s);
            Sessions[m.getHeader().m_From]->setTime(clock());
        }
        break;
    }
    default: {
        if (Sessions.find(m.getHeader().m_From) != Sessions.end()) {
            if (Sessions.find(m.getHeader().m_To) != Sessions.end()) {
                Sessions[m.getHeader().m_To]->Add(m);
            }
            else if (m.getHeader().m_To == A_ALL) {
                for (auto i : Sessions) {
                    if(i.first!=m.getHeader().m_From)
                        i.second->Add(m);
                }
                
            }
            Message::SendMessage(s, m.getHeader().m_From, A_BROCKER, M_CONFIRM);
            Sessions[m.getHeader().m_From]->setTime(clock());
        }
        break;
    }
    }
}



void start() {
    AfxSocketInit();
    CSocket Server;
    Server.Create(12345);

    thread tt(TimeOut);
    tt.detach();

    while (true)
    {
        Server.Listen();
        CSocket s;
        Server.Accept(s);
        thread t(ProcClient, s.Detach());
        t.detach();
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
            start();
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
