#pragma once

enum Adresses {
	A_BROCKER = 0,
	A_ALL = -1
};

enum MessageTypes {
	M_INIT,
	M_EXIT,
	M_CONFIRM,
	M_GETDATA,
	M_TEXT,
	M_NODATA
};

struct MsgHeader {
	int m_From;
	int m_To;
	int m_Type;
	int m_Size;
};

class Message {
private:
	MsgHeader m_Header;
	string m_Data;
public:
	MsgHeader getHeader() {
		return m_Header;
	}

	string getData() {
		return m_Data;
	}
	Message() {
		m_Header = { 0 };
		m_Data = "";
	}

	

	Message(int to, int from, int type = M_TEXT, const string& data = "") {
		m_Header.m_From = from;
		m_Header.m_To = to;
		m_Header.m_Type = type;
		m_Header.m_Size = data.length();
		m_Data = data;
	}

	void Send(CSocket& s) {
		s.Send(&m_Header, sizeof(MsgHeader));
		if (m_Header.m_Size != 0) {
			s.Send(m_Data.c_str(), m_Header.m_Size + 1);
		}
	}

	int Receive(CSocket& s) {
		s.Receive(&m_Header, sizeof(MsgHeader));
		if (m_Header.m_Size != 0) {
			char* pBuff = new char[m_Header.m_Size + 1];
			s.Receive(pBuff, m_Header.m_Size + 1);
			pBuff[m_Header.m_Size] = '\0';
			m_Data = pBuff;
			delete[] pBuff;
		}

		return m_Header.m_Type;
	}

	static void SendMessage(CSocket& s, int to, int from, int type = M_TEXT, const string& data = "") {
		Message m(to, from, type, data);
		m.Send(s);
	}
};