#include <fstream>
#include <iostream>
#include <string>
#include <vector>

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/internet-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/applications-module.h"
#include "ns3/error-model.h"
#include "ns3/tcp-header.h"
#include "ns3/udp-header.h"
#include "ns3/enum.h"
#include "ns3/event-id.h"
#include "ns3/flow-monitor-helper.h"
#include "ns3/ipv4-global-routing-helper.h"
#include "ns3/traffic-control-module.h"

using namespace ns3;

NS_LOG_COMPONENT_DEFINE ("Third_Question");

// ===========================================================================
//
//         node 0                 node 1
//   +----------------+    +----------------+
//   |    ns-3 TCP    |    |    ns-3 TCP    |
//   +----------------+    +----------------+
//   |    10.1.1.1    |    |    10.1.1.2    |
//   +----------------+    +----------------+
//   | point-to-point |    | point-to-point |
//   +----------------+    +----------------+
//           |                     |
//           +---------------------+
//                5 Mbps, 2 ms
//
//
// We want to look at changes in the ns-3 TCP congestion window.  We need
// to crank up a flow and hook the CongestionWindow attribute on the socket
// of the sender.  Normally one would use an on-off application to generate a
// flow, but this has a couple of problems.  First, the socket of the on-off
// application is not created until Application Start time, so we wouldn't be
// able to hook the socket (now) at configuration time.  Second, even if we
// could arrange a call after start time, the socket is not public so we
// couldn't get at it.
//
// So, we can cook up a simple version of the on-off application that does what
// we want.  On the plus side we don't need all of the complexity of the on-off
// application.  On the minus side, we don't have a helper, so we have to get
// a little more involved in the details, but this is trivial.
//
// So first, we create a socket and do the trace connect on it; then we pass
// this socket into the constructor of our simple application which we then
// install in the source node.
// ===========================================================================
//
class MyApp : public Application
{
public:
  MyApp ();
  virtual ~MyApp ();

  /**
   * Register this type.
   * \return The TypeId.
   */
  static TypeId GetTypeId (void);
  void Setup (Ptr<Socket> socket, Address address, uint32_t packetSize, uint32_t nPackets, DataRate dataRate);

private:
  virtual void StartApplication (void);
  virtual void StopApplication (void);

  void ScheduleTx (void);
  void SendPacket (void);

  Ptr<Socket>     m_socket;
  Address         m_peer;
  uint32_t        m_packetSize;
  uint32_t        m_nPackets;
  DataRate        m_dataRate;
  EventId         m_sendEvent;
  bool            m_running;
  uint32_t        m_packetsSent;
};

MyApp::MyApp ()
  : m_socket (0),
    m_peer (),
    m_packetSize (0),
    m_nPackets (0),
    m_dataRate (0),
    m_sendEvent (),
    m_running (false),
    m_packetsSent (0)
{
}

MyApp::~MyApp ()
{
  m_socket = 0;
}

/* static */
TypeId MyApp::GetTypeId (void)
{
  static TypeId tid = TypeId ("MyApp")
    .SetParent<Application> ()
    .SetGroupName ("Tutorial")
    .AddConstructor<MyApp> ()
    ;
  return tid;
}

void
MyApp::Setup (Ptr<Socket> socket, Address address, uint32_t packetSize, uint32_t nPackets, DataRate dataRate)
{
  m_socket = socket;
  m_peer = address;
  m_packetSize = packetSize;
  m_nPackets = nPackets;
  m_dataRate = dataRate;
}

void
MyApp::StartApplication (void)
{
  m_running = true;
  m_packetsSent = 0;
  if (InetSocketAddress::IsMatchingType (m_peer))
    {
      m_socket->Bind ();
    }
  else
    {
      m_socket->Bind6 ();
    }
  m_socket->Connect (m_peer);
  SendPacket ();
}

void
MyApp::StopApplication (void)
{
  m_running = false;

  if (m_sendEvent.IsRunning ())
    {
      Simulator::Cancel (m_sendEvent);
    }

  if (m_socket)
    {
      m_socket->Close ();
    }
}

void
MyApp::SendPacket (void)
{
  Ptr<Packet> packet = Create<Packet> (m_packetSize);
  m_socket->Send (packet);

  if (++m_packetsSent < m_nPackets)
    {
      ScheduleTx ();
    }
}

void
MyApp::ScheduleTx (void)
{
  if (m_running)
    {
      Time tNext (Seconds (m_packetSize * 8 / static_cast<double> (m_dataRate.GetBitRate ())));
      m_sendEvent = Simulator::Schedule (tNext, &MyApp::SendPacket, this);
    }
}

static void
CwndChange (Ptr<OutputStreamWrapper> stream, uint32_t oldCwnd, uint32_t newCwnd)
{
  NS_LOG_UNCOND (Simulator::Now ().GetSeconds () << "\t" << newCwnd); // For writing output on the console
  *stream->GetStream () << Simulator::Now ().GetSeconds () << "\t" << oldCwnd << "\t" << newCwnd << std::endl; // For writing in the output stream
}

static void
RxDrop (Ptr<PcapFileWrapper> file, Ptr<const Packet> p)
{
  NS_LOG_UNCOND ("RxDrop at " << Simulator::Now ().GetSeconds ());
  file->Write (Simulator::Now (), p);
}

int
main (int argc, char *argv[])
{  
//   bool useV6 = false;

  // Default configuration: All senders use TCP New Reno
  int configuration = 1;

  // Config 1: All senders use TCP New Reno
  // Config 2: Connection3 at TCP source uses the new congestion
  //           protocol TCPNewRenoCSE. The remaining senders use the default protocol TCPNewReno
  // Config 3: All senders use TCP NewRenoCSE

  CommandLine cmd;
  cmd.AddValue ("Configuration", "Configurations of the Network", configuration);
  cmd.Parse (argc, argv);

  std::string outputFile = "output3/q3";
  std::ofstream out(outputFile + "_" + std::to_string(configuration) + ".txt");

  // Print command goes here if you want to print anything on the console.
  //
  //

  // From here onwards, everything will be written to outputFile
  // Get the rdbuf of clog.
  // We need it to reset the value before exiting.
  auto old_rdbuf = std::clog.rdbuf();
  std::clog.rdbuf(out.rdbuf());

 //      DR = 10
 //   Prop Delay = 3ms
 // N1 ----------N3
 //              |
 //              |
 //              |  DR = 9
 //              |  Prop Delay = 3ms
 //              |
 //              N2


  NodeContainer nodes;
  nodes.Create (3);

  PointToPointHelper ptp1,ptp2;
  ptp1.SetDeviceAttribute ("DataRate", StringValue ("10Mbps"));
  ptp1.SetChannelAttribute ("Delay", StringValue ("3ms"));
  ptp2.SetDeviceAttribute ("DataRate", StringValue ("9Mbps"));
  ptp2.SetChannelAttribute ("Delay", StringValue ("3ms"));

  NetDeviceContainer devices13, devices23;
  devices13 = ptp1.Install (nodes.Get(0), nodes.Get(2));
  devices23 = ptp1.Install (nodes.Get(1), nodes.Get(2));

  Ptr<RateErrorModel> em = CreateObject<RateErrorModel> ();
  em->SetAttribute ("ErrorRate", DoubleValue (0.00001));
  devices13.Get(1)->SetAttribute ("ReceiveErrorModel", PointerValue (em));
  devices23.Get(1)->SetAttribute ("ReceiveErrorModel", PointerValue (em));

  InternetStackHelper stack;
  stack.Install (nodes);

  uint16_t sinkPort1 = 8080;
  uint16_t sinkPort2 = 8085;
  uint16_t sinkPort3 = 8090;
  
  Address sinkAddress1, sinkAddress2, sinkAddress3;
  Address anyAddress1, anyAddress2, anyAddress3;

  std::string probeType;
  std::string tracePath;

//   if (useV6 == false)
//     {
      Ipv4AddressHelper address;
      address.SetBase ("10.1.1.0", "255.255.255.0");

      Ipv4InterfaceContainer interfaces1 = address.Assign(devices13);
      address.SetBase ("10.1.2.0", "255.255.255.0");
      Ipv4InterfaceContainer interfaces2 = address.Assign(devices23);

      sinkAddress1 = InetSocketAddress (interfaces1.GetAddress (1), sinkPort1);
      sinkAddress2 = InetSocketAddress (interfaces1.GetAddress (1), sinkPort2);
      sinkAddress3 = InetSocketAddress (interfaces2.GetAddress (1), sinkPort3);
      
      anyAddress1 = InetSocketAddress (Ipv4Address::GetAny (), sinkPort1);
      anyAddress2 = InetSocketAddress (Ipv4Address::GetAny (), sinkPort2);
      anyAddress3 = InetSocketAddress (Ipv4Address::GetAny (), sinkPort3);

      PacketSinkHelper packetSinkHelper1 ("ns3::TcpSocketFactory", anyAddress1);
      PacketSinkHelper packetSinkHelper2 ("ns3::TcpSocketFactory", anyAddress2);
      PacketSinkHelper packetSinkHelper3 ("ns3::TcpSocketFactory", anyAddress3);

      probeType = "ns3::Ipv4PacketProbe";
      tracePath = "/NodeList/*/$ns3::Ipv4L3Protocol/Tx";
    // }
//   else
//     {
//     //   Ipv6AddressHelper address;
//     //   address.SetBase ("2001:0000:f00d:cafe::", Ipv6Prefix (64));
//     //   Ipv6InterfaceContainer interfaces = address.Assign (devices);
//     //   sinkAddress = Inet6SocketAddress (interfaces.GetAddress (1,1), sinkPort);
//     //   anyAddress = Inet6SocketAddress (Ipv6Address::GetAny (), sinkPort);
//     //   probeType = "ns3::Ipv6PacketProbe";
//     //   tracePath = "/NodeList/*/$ns3::Ipv6L3Protocol/Tx";
//     }

  // All sinks are at Node(2) i.e. N2
  ApplicationContainer sinkApps1 = packetSinkHelper1.Install (nodes.Get (2));
  ApplicationContainer sinkApps2 = packetSinkHelper2.Install (nodes.Get (2));
  ApplicationContainer sinkApps3 = packetSinkHelper3.Install (nodes.Get (2));

  sinkApps1.Start (Seconds (0.0));
  sinkApps1.Stop (Seconds (30.0));
  sinkApps2.Start (Seconds (0.0));
  sinkApps2.Stop (Seconds (30.0));
  sinkApps3.Start (Seconds (0.0));
  sinkApps3.Stop (Seconds (30.0));

  std::stringstream node1, node2, node3;
  node1 << nodes.Get (0)->GetId ();
  node2 << nodes.Get (1)->GetId ();
  node3 << nodes.Get (2)->GetId ();

  std::string node1_str = "/NodeList/" + node1.str() + "/$ns3::TcpL4Protocol/SocketType";
  std::string node2_str = "/NodeList/" + node2.str() + "/$ns3::TcpL4Protocol/SocketType";
  std::string node3_str = "/NodeList/" + node3.str() + "/$ns3::TcpL4Protocol/SocketType";

  TypeIdValue TcpNewReno_config = TypeIdValue (TypeId::LookupByName ("ns3::TcpNewReno"));
  TypeIdValue TcpNewRenoCSE_config = TypeIdValue (TypeId::LookupByName ("ns3::TcpNewRenoCSE"));

  if (configuration == 1)
  {
      Config::Set(node1_str, TcpNewReno_config);
      Config::Set(node2_str, TcpNewReno_config);
      Config::Set(node3_str, TcpNewReno_config);
  }
  else if(configuration == 2)
  {
      Config::Set(node1_str, TcpNewReno_config);
      Config::Set(node2_str, TcpNewReno_config);
      Config::Set(node3_str, TcpNewRenoCSE_config);
  }
  else
  {
      Config::Set(node1_str, TcpNewRenoCSE_config);
      Config::Set(node2_str, TcpNewRenoCSE_config);
      Config::Set(node3_str, TcpNewRenoCSE_config);
  }

  // Three TCP sockets  starting from source (will connect them with sink)
  // 2 TCP sockets starting N1 and 1 from N2
  Ptr<Socket> ns3TcpSocket1 = Socket::CreateSocket (nodes.Get (0), TcpSocketFactory::GetTypeId ());
  Ptr<Socket> ns3TcpSocket2 = Socket::CreateSocket (nodes.Get (0), TcpSocketFactory::GetTypeId ());
  Ptr<Socket> ns3TcpSocket3 = Socket::CreateSocket (nodes.Get (1), TcpSocketFactory::GetTypeId ());
  

  Ptr<MyApp> app1 = CreateObject<MyApp> ();
  Ptr<MyApp> app2 = CreateObject<MyApp> ();
  Ptr<MyApp> app3 = CreateObject<MyApp> ();

  int NumOfPackets = 100000;
  int PacketSize   = 3000;
  std::string ApplicationDataRate = "1.5Mbps";

  app1->Setup (ns3TcpSocket1, sinkAddress1, PacketSize, NumOfPackets, DataRate (ApplicationDataRate));
  nodes.Get (0)->AddApplication(app1);
  app1->SetStartTime (Seconds (1.0));
  app1->SetStopTime (Seconds (20.0));

  app2->Setup (ns3TcpSocket2, sinkAddress2, PacketSize, NumOfPackets, DataRate (ApplicationDataRate));
  nodes.Get (0)->AddApplication(app2);
  app2->SetStartTime (Seconds (5.0));
  app2->SetStopTime (Seconds (25.0));

  app3->Setup (ns3TcpSocket3, sinkAddress3, PacketSize, NumOfPackets, DataRate (ApplicationDataRate));
  nodes.Get (0)->AddApplication(app3);
  app3->SetStartTime (Seconds (15.0));
  app3->SetStopTime (Seconds (30.0));

//   app->Setup (ns3TcpSocket, sinkAddress1, 1040, 1000, DataRate ("1Mbps"));
//   nodes.Get (0)->AddApplication (app);
//   app->SetStartTime (Seconds (1.));
//   app->SetStopTime (Seconds (20.));

  AsciiTraceHelper asciiTraceHelper;
  std::string temp = outputFile + "_" + std::to_string(configuration) + "_";
  Ptr<OutputStreamWrapper> stream1 = asciiTraceHelper.CreateFileStream (temp + "1.cwnd");
  Ptr<OutputStreamWrapper> stream2 = asciiTraceHelper.CreateFileStream (temp + "2.cwnd");
  Ptr<OutputStreamWrapper> stream3 = asciiTraceHelper.CreateFileStream (temp + "3.cwnd");

  ns3TcpSocket1->TraceConnectWithoutContext ("CongestionWindow", MakeBoundCallback (&CwndChange, stream1));
  ns3TcpSocket2->TraceConnectWithoutContext ("CongestionWindow", MakeBoundCallback (&CwndChange, stream2));
  ns3TcpSocket3->TraceConnectWithoutContext ("CongestionWindow", MakeBoundCallback (&CwndChange, stream3));

  PcapHelper pcapHelper;
  Ptr<PcapFileWrapper> file1 = pcapHelper.CreateFile (temp + "1.pcap", std::ios::out, PcapHelper::DLT_PPP);
  Ptr<PcapFileWrapper> file2 = pcapHelper.CreateFile (temp + "2.pcap", std::ios::out, PcapHelper::DLT_PPP);
  Ptr<PcapFileWrapper> file3 = pcapHelper.CreateFile (temp + "3.pcap", std::ios::out, PcapHelper::DLT_PPP);

  devices13.Get (1)->TraceConnectWithoutContext ("PhyRxDrop", MakeBoundCallback (&RxDrop, file1));
  devices13.Get (1)->TraceConnectWithoutContext ("PhyRxDrop", MakeBoundCallback (&RxDrop, file2));
  devices23.Get (1)->TraceConnectWithoutContext ("PhyRxDrop", MakeBoundCallback (&RxDrop, file3));

  Simulator::Stop (Seconds (30.0));
  Simulator::Run ();
  Simulator::Destroy ();

  // Reset the rdbuf of clog.
  std::clog.rdbuf(old_rdbuf);

  return 0;
}

