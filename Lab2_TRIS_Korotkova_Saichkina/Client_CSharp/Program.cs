using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Net;
using System.Net.Sockets;
using System.Threading;

namespace Client_CSharp
{
    class Program
    {
        
        static int MyID;

        public enum Adresses
        {
            A_BROCKER = 0,
            A_ALL = -1
        }
        public enum MessageTypes
        {
            M_INIT,
            M_EXIT,
            M_CONFIRM,
            M_GETDATA,
            M_TEXT,
            M_NODATA
        }
        public struct MsgHeader
        {
            public int m_From;
            public int m_To;
            public MessageTypes m_Type;
            public int m_Size;
        }

        public class Message
        {
            private MsgHeader m_Header;
            private string m_Data;

            public MsgHeader getM_Header()
            {
                return m_Header;
            }

            public void setM_Data(string d)
            {
                m_Data = d;
            }

            public string getM_Data()
            {
                return m_Data;
            }

            public Message()
            {
                m_Header.m_To = 0;
                m_Header.m_From = 0;
                m_Header.m_Size = 0;
                m_Header.m_Type = 0;
            }

            public Message(int To, int From, MessageTypes Type= MessageTypes.M_TEXT, string data = "")
            {
                m_Header.m_To = To;
                m_Header.m_From = From;
                m_Header.m_Type = Type;
                m_Header.m_Size = data.Length;
                m_Data = data;
            }

            public void Send(Socket s)
            {
                
                s.Send(BitConverter.GetBytes(m_Header.m_From), sizeof(int), SocketFlags.None);
                s.Send(BitConverter.GetBytes(m_Header.m_To), sizeof(int), SocketFlags.None);
                s.Send(BitConverter.GetBytes((int)m_Header.m_Type), sizeof(int), SocketFlags.None);
                s.Send(BitConverter.GetBytes(m_Header.m_Size), sizeof(int), SocketFlags.None);
                
                if (m_Header.m_Size != 0)
                {
                    s.Send(Encoding.UTF8.GetBytes(m_Data), m_Header.m_Size, SocketFlags.None);
                }

            }

            public MessageTypes Receive(Socket s)
            {

                byte[] b = new byte[4];
                s.Receive(b, sizeof(int), SocketFlags.None);
                m_Header.m_From = BitConverter.ToInt32(b, 0);

                b = new byte[4];
                s.Receive(b, sizeof(int), SocketFlags.None);
                m_Header.m_To = BitConverter.ToInt32(b, 0);

                b = new byte[4];
                s.Receive(b, sizeof(int), SocketFlags.None);
                m_Header.m_Type = (MessageTypes)BitConverter.ToInt32(b, 0);

                b = new byte[4];
                s.Receive(b, sizeof(int), SocketFlags.None);
                m_Header.m_Size = BitConverter.ToInt32(b, 0);

                if (m_Header.m_Size != 0)
                {
                    b = new byte[m_Header.m_Size];
                    s.Receive(b, m_Header.m_Size, SocketFlags.None);
                    m_Data = Encoding.UTF8.GetString(b, 0, m_Header.m_Size);
                }

                return m_Header.m_Type;
            }

            

        };
        static void SendMessage(Socket s, int To, int From, MessageTypes Type = MessageTypes.M_TEXT, string Data = "")
        {
            Message m = new Message(To, From, Type, Data);
            m.Send(s);
        }

        static void connect(Socket s, IPEndPoint endPoint)
        {
            s.Connect(endPoint);
        }

        static void disconnect(Socket s)
        {
            s.Shutdown(SocketShutdown.Both);
            s.Close();
        }

        //ПРОВЕРКА НА НАЛИЧИЕ ДАННЫХ
        static void GetData()
        {
            while (true)
            {
                IPEndPoint endPoint = new IPEndPoint(IPAddress.Parse("127.0.0.1"), 12345);
                Socket s = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
                Message m = new Message();

                connect(s, endPoint);
                SendMessage(s, 0, MyID, MessageTypes.M_GETDATA);
                if (m.Receive(s) == MessageTypes.M_TEXT)
                {
                    Console.WriteLine("Message from client " + m.getM_Header().m_From + ": " + m.getM_Data());
                }
                disconnect(s);
                Thread.Sleep(1000);
            }
        }


        static void Main(string[] args)
        {
            Message m = new Message();
            IPEndPoint endPoint = new IPEndPoint(IPAddress.Parse("127.0.0.1"), 12345);
            Socket s = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);

            //Подключение к серверу
            connect(s, endPoint);
            if (!s.Connected)
                return;

            SendMessage(s, (int)Adresses.A_BROCKER, 0, MessageTypes.M_INIT);
            if (m.Receive(s) == MessageTypes.M_CONFIRM)
            {
                MyID = m.getM_Header().m_To;
                Console.WriteLine("My id is "+MyID);
                Thread t = new Thread(GetData);
                t.Start();
            }
            disconnect(s);

            //ОТПРАВКА СООБЩЕНИЙ
            while (true)
            {
                endPoint = new IPEndPoint(IPAddress.Parse("127.0.0.1"), 12345);
                s = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
                Console.WriteLine("1. Send Message\n2. Exit\n");
                int choice = Convert.ToInt32(Console.ReadLine());
                switch (choice)
                {
                    case 1:
                        {
                            int ClientID = (int)Adresses.A_ALL;
                            Console.WriteLine("1. Only for one client\n2.For All Clients\n");
                            int choice2 = Convert.ToInt32(Console.ReadLine());
                            if (choice2 == 1)
                            {
                                Console.WriteLine("Enter ID of Client");
                                ClientID = Convert.ToInt32(Console.ReadLine());
                            }

                            Console.WriteLine("Enter your message");
                            string str = Console.ReadLine().ToString();
                            connect(s, endPoint);
                            SendMessage(s, ClientID, MyID, MessageTypes.M_TEXT, str);
                            if (m.Receive(s) == MessageTypes.M_CONFIRM)
                            {
                                Console.WriteLine("succes");
                            }
                            else
                            {
                                Console.WriteLine("error");
                            }
                            disconnect(s);
                            break;

                        }
                    case 2:
                        {
                            connect(s, endPoint);
                            SendMessage(s, (int)Adresses.A_BROCKER, MyID, MessageTypes.M_EXIT);
                            if (m.Receive(s) == MessageTypes.M_CONFIRM)
                            {
                                Console.WriteLine("succes");
                            }
                            else
                            {
                                Console.WriteLine("error");
                            }
                            
                            disconnect(s);
                            Environment.Exit(0);
                            break;
                        }

                    default:
                        break;
                }
            }
        }
    }
}
