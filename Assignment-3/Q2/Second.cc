// /* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
// /*
//  * This program is free software; you can redistribute it and/or modify
//  * it under the terms of the GNU General Public License version 2 as
//  * published by the Free Software Foundation;
//  *
//  * This program is distributed in the hope that it will be useful,
//  * but WITHOUT ANY WARRANTY; without even the implied warranty of
//  * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  * GNU General Public License for more details.
//  *
//  * You should have received a copy of the GNU General Public License
//  * along with this program; if not, write to the Free Software
//  * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//  */


// #include <fstream>
// #include "ns3/core-module.h"
// #include "ns3/network-module.h"
// #include "ns3/internet-module.h"
// #include "ns3/point-to-point-module.h"
// #include "ns3/applications-module.h"

// // #include <string>
// // #include <iostream>
// // #include <fstream>
// // #include <string>
// // #include <vector>


// using namespace ns3;

// NS_LOG_COMPONENT_DEFINE ("Second_Question");

// // ===========================================================================
// //
// //         node 0                 node 1
// //   +----------------+    +----------------+
// //   |    ns-3 TCP    |    |    ns-3 TCP    |
// //   +----------------+    +----------------+
// //   |    10.1.1.1    |    |    10.1.1.2    |
// //   +----------------+    +----------------+
// //   | point-to-point |    | point-to-point |
// //   +----------------+    +----------------+
// //           |                     |
// //           +---------------------+
// //                2 Mbps, 3 ms

// class MyApp : public Application
// {
// public:
//   MyApp ();
//   virtual ~MyApp ();

//   /**
//    * Register this type.
//    * \return The TypeId.
//    */
//   static TypeId GetTypeId (void);
//   void Setup (Ptr<Socket> socket, Address address, uint32_t packetSize, uint32_t nPackets, DataRate dataRate);

// private:
//   virtual void StartApplication (void);
//   virtual void StopApplication (void);

//   void ScheduleTx (void);
//   void SendPacket (void);

//   Ptr<Socket>     m_socket;
//   Address         m_peer;
//   uint32_t        m_packetSize;
//   uint32_t        m_nPackets;
//   DataRate        m_dataRate;
//   EventId         m_sendEvent;
//   bool            m_running;
//   uint32_t        m_packetsSent;
// };

// MyApp::MyApp ()
//   : m_socket (0),
//     m_peer (),
//     m_packetSize (0),
//     m_nPackets (0),
//     m_dataRate (0),
//     m_sendEvent (),
//     m_running (false),
//     m_packetsSent (0)
// {
// }

// MyApp::~MyApp ()
// {
//   m_socket = 0;
// }

// /* static */
// TypeId MyApp::GetTypeId (void)
// {
//   static TypeId tid = TypeId ("MyApp")
//     .SetParent<Application> ()
//     .SetGroupName ("Tutorial")
//     .AddConstructor<MyApp> ()
//     ;
//   return tid;
// }

// void
// MyApp::Setup (Ptr<Socket> socket, Address address, uint32_t packetSize, uint32_t nPackets, DataRate dataRate)
// {
//   m_socket = socket;
//   m_peer = address;
//   m_packetSize = packetSize;
//   m_nPackets = nPackets;
//   m_dataRate = dataRate;
// }

// void
// MyApp::StartApplication (void)
// {
//   m_running = true;
//   m_packetsSent = 0;
//   if (InetSocketAddress::IsMatchingType (m_peer))
//     {
//       m_socket->Bind ();
//     }
//   else
//     {
//       m_socket->Bind6 ();
//     }
//   m_socket->Connect (m_peer);
//   SendPacket ();
// }

// void
// MyApp::StopApplication (void)
// {
//   m_running = false;

//   if (m_sendEvent.IsRunning ())
//     {
//       Simulator::Cancel (m_sendEvent);
//     }

//   if (m_socket)
//     {
//       m_socket->Close ();
//     }
// }

// void
// MyApp::SendPacket (void)
// {
//   Ptr<Packet> packet = Create<Packet> (m_packetSize);
//   m_socket->Send (packet);

//   if (++m_packetsSent < m_nPackets)
//     {
//       ScheduleTx ();
//     }
// }

// void
// MyApp::ScheduleTx (void)
// {
//   if (m_running)
//     {
//       Time tNext (Seconds (m_packetSize * 8 / static_cast<double> (m_dataRate.GetBitRate ())));
//       m_sendEvent = Simulator::Schedule (tNext, &MyApp::SendPacket, this);
//     }
// }

// static void
// CwndChange (Ptr<OutputStreamWrapper> stream, uint32_t oldCwnd, uint32_t newCwnd)
// {
//   NS_LOG_UNCOND (Simulator::Now ().GetSeconds () << "\t" << newCwnd);
//   *stream->GetStream () << Simulator::Now ().GetSeconds () << "\t" << oldCwnd << "\t" << newCwnd << std::endl;
// }

// static void
// RxDrop (Ptr<OutputStreamWrapper> stream,Ptr<const Packet> p)
// {
//   NS_LOG_UNCOND ("RxDrop at " << Simulator::Now ().GetSeconds ());
//   *stream->GetStream () << Simulator::Now ().GetSeconds () << "\t" << "RxDrop" << std::endl;  
// }

// int
// main (int argc, char *argv[])
// {

//   CommandLine cmd;

//   std::string cdr_val = "6Mbps";
//   cmd.AddValue ("CDR","Channel Data Rate",cdr_val);

//   std::string adr_val = "2Mbps";
//   cmd.AddValue ("ADR","Application Data Rate",adr_val);

//   cmd.Parse (argc, argv);

//   std::ofstream out("../output/q2_cdr_" + cdr_val + "_adr_" + adr_val + ".txt");

//   // Get the rdbuf of clog.
//   // We need it to reset the value before exiting.
//   auto old_rdbuf = std::clog.rdbuf();

//   // Set the rdbuf of clog.
//   std::clog.rdbuf(out.rdbuf());

//   // Write to clog.
//   // The output should go to test.txt

//   Config::SetDefault ("ns3::TcpL4Protocol::SocketType", TypeIdValue (TcpNewReno::GetTypeId ()));


//   // CDR: (2Mbps, 4Mbps, 10 Mbps, 20Mbps, 50 Mbps) at ADR-2Mbps
//   // ADR: (0.5 Mbps, 1Mbps, 2Mbps, 4Mbps, 10 Mbps) at CDR-6Mbps

  
//   NodeContainer nodes;
//   nodes.Create (2);

//   PointToPointHelper pointToPoint;
//   pointToPoint.SetDeviceAttribute ("DataRate", StringValue (cdr_val));
//   pointToPoint.SetChannelAttribute ("Delay", StringValue ("3ms"));

//   NetDeviceContainer devices;
//   devices = pointToPoint.Install (nodes);

//   Ptr<RateErrorModel> em = CreateObject<RateErrorModel> ();
//   em->SetAttribute ("ErrorRate", DoubleValue (0.00001));
//   devices.Get (1)->SetAttribute ("ReceiveErrorModel", PointerValue (em));

//   InternetStackHelper stack;
//   stack.Install (nodes);

  
//   Address anyAddress;
//   std::string probeType;
//   std::string tracePath;

//   Ipv4AddressHelper address;
//   address.SetBase ("10.1.1.0", "255.255.255.0");
//   Ipv4InterfaceContainer interfaces = address.Assign (devices);

//   uint16_t sinkPort = 8080;
//   Address sinkAddress = InetSocketAddress (interfaces.GetAddress (1), sinkPort);
//   anyAddress = InetSocketAddress (Ipv4Address::GetAny (), sinkPort);
//   probeType = "ns3::Ipv4PacketProbe";
//   tracePath = "/NodeList/*/$ns3::Ipv4L3Protocol/Tx";

//   PacketSinkHelper packetSinkHelper ("ns3::TcpSocketFactory", anyAddress);
//   ApplicationContainer sinkApps = packetSinkHelper.Install (nodes.Get (1));
//   sinkApps.Start (Seconds (1.0));
//   sinkApps.Stop (Seconds (30.0));

//   Ptr<Socket> ns3TcpSocket = Socket::CreateSocket (nodes.Get (0), TcpSocketFactory::GetTypeId ());

//   Ptr<MyApp> app = CreateObject<MyApp> ();

//   // Packet Size is 3000 bytes
//   // Send 100000 packets
//   app->Setup (ns3TcpSocket, sinkAddress, 3000, 100000, DataRate (adr_val));
  
//   nodes.Get (0)->AddApplication (app);
//   app->SetStartTime (Seconds (1.0));
//   app->SetStopTime (Seconds (30.0));

//   AsciiTraceHelper asciiTraceHelper;
//   Ptr<OutputStreamWrapper> stream = asciiTraceHelper.CreateFileStream ("seventh_1.cwnd");
//   ns3TcpSocket->TraceConnectWithoutContext ("CongestionWindow", MakeBoundCallback (&CwndChange, stream));

//   PcapHelper pcapHelper;
//   Ptr<PcapFileWrapper> file1 = pcapHelper.CreateFile ("seventh_2.pcap", std::ios::out, PcapHelper::DLT_PPP);
//   devices.Get (1)->TraceConnectWithoutContext ("PhyRxDrop", MakeBoundCallback (&RxDrop, file1));

//   Simulator::Stop (Seconds (30.0));

//   Simulator::Run ();
//   Simulator::Destroy ();

//   // Reset the rdbuf of clog.
//   std::clog.rdbuf(old_rdbuf);

//   return 0;
// }


/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
/*
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation;
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

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

NS_LOG_COMPONENT_DEFINE ("First_Question");

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
  m_socket->Bind ();
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
  NS_LOG_UNCOND (Simulator::Now ().GetSeconds () << "\t" << newCwnd);
  *stream->GetStream () << Simulator::Now ().GetSeconds () << "\t" << oldCwnd << "\t" << newCwnd << std::endl;
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
  CommandLine cmd;

  std::string cdr_val = "6Mbps";
  cmd.AddValue ("CDR","Channel Data Rate",cdr_val);

  std::string adr_val = "10Mbps";
  cmd.AddValue ("ADR","Application Data Rate",adr_val);

  cmd.Parse (argc, argv);

  // CDR: (2Mbps, 4Mbps, 10 Mbps, 20Mbps, 50 Mbps) at ADR-2Mbps
  // ADR: (0.5 Mbps, 1Mbps, 2Mbps, 4Mbps, 10 Mbps) at CDR-6Mbps

  std::string outputFile = "output2/q2_cdr_" + cdr_val + "_adr_" + adr_val;
  std::ofstream out(outputFile + ".txt");

  std::cout << "Channel Data Rate: " << cdr_val << ", Application Data Rate:" << adr_val << std::endl;

  // Get the rdbuf of clog.
  // We need it to reset the value before exiting.
  auto old_rdbuf = std::clog.rdbuf();
  std::clog.rdbuf(out.rdbuf());

  Config::SetDefault ("ns3::TcpL4Protocol::SocketType", TypeIdValue (TcpNewReno::GetTypeId ()));  

  
  NodeContainer nodes;
  nodes.Create (2);

  PointToPointHelper pointToPoint;
  pointToPoint.SetDeviceAttribute ("DataRate", StringValue (cdr_val));
  pointToPoint.SetChannelAttribute ("Delay", StringValue ("3ms"));

  NetDeviceContainer devices;
  devices = pointToPoint.Install (nodes);

  Ptr<RateErrorModel> em = CreateObject<RateErrorModel> ();
  em->SetAttribute ("ErrorRate", DoubleValue (0.00001));
  devices.Get (1)->SetAttribute ("ReceiveErrorModel", PointerValue (em));

  InternetStackHelper stack;
  stack.Install (nodes);

  Address anyAddress;
  std::string probeType;
  std::string tracePath;

  Ipv4AddressHelper address;
  address.SetBase ("10.1.1.0", "255.255.255.0");
  Ipv4InterfaceContainer interfaces = address.Assign (devices);

  uint16_t sinkPort = 8080;
  Address sinkAddress = InetSocketAddress (interfaces.GetAddress (1), sinkPort);
  anyAddress = InetSocketAddress (Ipv4Address::GetAny (), sinkPort);
  probeType = "ns3::Ipv4PacketProbe";
  tracePath = "/NodeList/*/$ns3::Ipv4L3Protocol/Tx";

  PacketSinkHelper packetSinkHelper ("ns3::TcpSocketFactory", anyAddress);
  ApplicationContainer sinkApps = packetSinkHelper.Install (nodes.Get (1));
  sinkApps.Start (Seconds (1.0));
  sinkApps.Stop (Seconds (30.0));

  Ptr<Socket> ns3TcpSocket = Socket::CreateSocket (nodes.Get (0), TcpSocketFactory::GetTypeId ());

  Ptr<MyApp> app = CreateObject<MyApp> ();

  // Packet Size is 3000 bytes
  // Send 100000 packets
  app->Setup (ns3TcpSocket, sinkAddress, 3000, 100000, DataRate (adr_val));
  
  nodes.Get (0)->AddApplication (app);
  app->SetStartTime (Seconds (1.0));
  app->SetStopTime (Seconds (30.0));

  AsciiTraceHelper asciiTraceHelper;
  
  std::string output2 = outputFile + ".cwnd";
  Ptr<OutputStreamWrapper> stream = asciiTraceHelper.CreateFileStream (outputFile + ".cwnd");
  ns3TcpSocket->TraceConnectWithoutContext ("CongestionWindow", MakeBoundCallback (&CwndChange, stream));

  PcapHelper pcapHelper;
  Ptr<PcapFileWrapper> file1 = pcapHelper.CreateFile ("seventh_2.pcap", std::ios::out, PcapHelper::DLT_PPP);
  devices.Get (1)->TraceConnectWithoutContext ("PhyRxDrop", MakeBoundCallback (&RxDrop, file1));

  Simulator::Stop (Seconds (30.0));

  Simulator::Run ();
  Simulator::Destroy ();

  // Reset the rdbuf of clog.
  std::clog.rdbuf(old_rdbuf);

  return 0;
}

