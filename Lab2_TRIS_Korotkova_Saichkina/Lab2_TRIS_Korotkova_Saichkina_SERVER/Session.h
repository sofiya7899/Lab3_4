#pragma once

class Session {
private:
	int s_id;
	queue<Message> messages;
	CRITICAL_SECTION m_CS;
	clock_t  time; //Последнее время активности клиента
public:
	int getId() {
		return s_id;
	}
	void setId(int i) {
		s_id = i;
	}

	void setTime(clock_t t) {
		time = t;
	}
	clock_t getTime() {
		return time;
	}

	Session(int ID, clock_t t)
		:s_id(ID), time(t) {
		InitializeCriticalSection(&m_CS);
	}
	Session() {
		InitializeCriticalSection(&m_CS);
	}
	~Session() {
		DeleteCriticalSection(&m_CS);
	}

	void Add(Message& m) {
		EnterCriticalSection(&m_CS);
		messages.push(m);
		LeaveCriticalSection(&m_CS);
	}

	void Send(CSocket& s) {
		EnterCriticalSection(&m_CS);
		if (messages.empty())
		{
			Message::SendMessage(s, s_id, A_BROCKER, M_NODATA);
		}
		else
		{
			messages.front().Send(s);
			messages.pop();
		}
		LeaveCriticalSection(&m_CS);
	}
};
