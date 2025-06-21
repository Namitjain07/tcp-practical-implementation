#include <fstream>
#include <sys/stat.h> // For creating directory
#include <sys/types.h>
#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/internet-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/applications-module.h"

using namespace ns3;

NS_LOG_COMPONENT_DEFINE("TcpExample");

class MyApp : public Application
{
public:
  MyApp();
  virtual ~MyApp();

  void Setup(Ptr<Socket> socket, Address address, uint32_t packetSize, uint32_t nPackets, DataRate dataRate);

private:
  virtual void StartApplication(void);
  virtual void StopApplication(void);

  void ScheduleTx(void);
  void SendPacket(void);

  Ptr<Socket> m_socket;
  Address m_peer;
  uint32_t m_packetSize;
  uint32_t m_nPackets;
  DataRate m_dataRate;
  EventId m_sendEvent;
  bool m_running;
  uint32_t m_packetsSent;
};

MyApp::MyApp()
  : m_socket(0),
    m_peer(),
    m_packetSize(0),
    m_nPackets(0),
    m_dataRate(0),
    m_sendEvent(),
    m_running(false),
    m_packetsSent(0)
{
}

MyApp::~MyApp()
{
  m_socket = 0;
}

void MyApp::Setup(Ptr<Socket> socket, Address address, uint32_t packetSize, uint32_t nPackets, DataRate dataRate)
{
  m_socket = socket;
  m_peer = address;
  m_packetSize = packetSize;
  m_nPackets = nPackets;
  m_dataRate = dataRate;
}

void MyApp::StartApplication(void)
{
  m_running = true;
  m_packetsSent = 0;
  m_socket->Bind();
  m_socket->Connect(m_peer);
  SendPacket();
}

void MyApp::StopApplication(void)
{
  m_running = false;

  if (m_sendEvent.IsRunning())
  {
    Simulator::Cancel(m_sendEvent);
  }

  if (m_socket)
  {
    m_socket->Close();
  }
}

void MyApp::SendPacket(void)
{
  Ptr<Packet> packet = Create<Packet>(m_packetSize);
  m_socket->Send(packet);

  if (++m_packetsSent < m_nPackets)
  {
    ScheduleTx();
  }
}

void MyApp::ScheduleTx(void)
{
  if (m_running)
  {
    Time tNext(Seconds(m_packetSize * 8 / static_cast<double>(m_dataRate.GetBitRate())));
    m_sendEvent = Simulator::Schedule(tNext, &MyApp::SendPacket, this);
  }
}

static void CwndChange(Ptr<OutputStreamWrapper> stream, uint32_t oldCwnd, uint32_t newCwnd)
{
  *stream->GetStream() << Simulator::Now().GetSeconds() << "\t" << oldCwnd << "\t" << newCwnd << std::endl;
}

int main(int argc, char *argv[])
{
  // Initialize parameters
  std::string tcp_variant = "TcpNewReno";
  std::string bandwidth_n0n1 = "10Mbps";
  std::string delay_n0n1 = "100ms";
  std::string bandwidth_n1n2 = "7Mbps";
  std::string delay_n1n2 = "10ms";
  std::string queuesize = "50p";
  double error_rate = 0.000001;
  int simulation_time = 10; // seconds
  uint32_t payload_size = 1460; // bytes

  // Create the output directory
  std::string output_folder = "output-tcp";
  mkdir(output_folder.c_str(), 0777); // Creates folder if it does not exist

  // Set TCP and Queue parameters
  Config::SetDefault("ns3::TcpL4Protocol::SocketType", StringValue("ns3::" + tcp_variant));

  // Create nodes
  NodeContainer n0n1;
  n0n1.Create(2);

  // Configure Point-to-Point link for n0n1
  PointToPointHelper point_to_point_n0n1;
  point_to_point_n0n1.SetDeviceAttribute("DataRate", StringValue(bandwidth_n0n1));
  point_to_point_n0n1.SetChannelAttribute("Delay", StringValue(delay_n0n1));
  NetDeviceContainer devices_n0n1 = point_to_point_n0n1.Install(n0n1);

  // Set the queue size of Node 1
  Ptr<PointToPointNetDevice> deviceNode1 = devices_n0n1.Get(1)->GetObject<PointToPointNetDevice>();
  Ptr<Queue<Packet>> queue = deviceNode1->GetQueue();
  queue->SetMaxSize(QueueSize(queuesize));

  // Create and configure the second link n1n2
  NodeContainer n1n2;
  n1n2.Add(n0n1.Get(1));
  n1n2.Create(1);

  PointToPointHelper point_to_point_n1n2;
  point_to_point_n1n2.SetDeviceAttribute("DataRate", StringValue(bandwidth_n1n2));
  point_to_point_n1n2.SetChannelAttribute("Delay", StringValue(delay_n1n2));
  NetDeviceContainer devices_n1n2 = point_to_point_n1n2.Install(n1n2);

  // Error model configuration
  Ptr<RateErrorModel> em = CreateObject<RateErrorModel>();
  em->SetAttribute("ErrorRate", DoubleValue(error_rate));
  devices_n0n1.Get(0)->SetAttribute("ReceiveErrorModel", PointerValue(em));
  devices_n0n1.Get(1)->SetAttribute("ReceiveErrorModel", PointerValue(em));
  devices_n1n2.Get(0)->SetAttribute("ReceiveErrorModel", PointerValue(em));
  devices_n1n2.Get(1)->SetAttribute("ReceiveErrorModel", PointerValue(em));

  // Install network stack
  InternetStackHelper stack;
  stack.InstallAll();

  // Assign IP addresses
  Ipv4AddressHelper address;
  address.SetBase("10.1.1.0", "255.255.255.0");
  Ipv4InterfaceContainer interfaces_n0n1 = address.Assign(devices_n0n1);

  address.SetBase("10.1.2.0", "255.255.255.0");
  Ipv4InterfaceContainer interfaces_n1n2 = address.Assign(devices_n1n2);

  Ipv4GlobalRoutingHelper::PopulateRoutingTables();

  // PacketSink setup
  uint16_t sinkPort = 8080;
  Address sinkAddress(InetSocketAddress(interfaces_n1n2.GetAddress(1), sinkPort));
  PacketSinkHelper packetSinkHelper("ns3::TcpSocketFactory", InetSocketAddress(Ipv4Address::GetAny(), sinkPort));
  ApplicationContainer sinkApps = packetSinkHelper.Install(n1n2.Get(1));
  sinkApps.Start(Seconds(0.0));
  sinkApps.Stop(Seconds(simulation_time));

  // Sender setup
  Ptr<Socket> source = Socket::CreateSocket(n0n1.Get(0), TcpSocketFactory::GetTypeId());

  Ptr<MyApp> app = CreateObject<MyApp>();
  app->Setup(source, sinkAddress, payload_size, 1000000, DataRate("100Mbps"));
  n0n1.Get(0)->AddApplication(app);
  app->SetStartTime(Seconds(1.0));
  app->SetStopTime(Seconds(simulation_time));

  // Congestion window tracing
  AsciiTraceHelper asciiTraceHelper;
  std::string cwnd_file = output_folder + "/tcp-example.cwnd";
  Ptr<OutputStreamWrapper> stream = asciiTraceHelper.CreateFileStream(cwnd_file);
  source->TraceConnectWithoutContext("CongestionWindow", MakeBoundCallback(&CwndChange, stream));

  // ASCII and PCAP traces
  std::string ascii_file = output_folder + "/tcp-example.tr";
  std::string pcap_prefix = output_folder + "/tcp-example";
  point_to_point_n0n1.EnableAsciiAll(asciiTraceHelper.CreateFileStream(ascii_file));
  point_to_point_n0n1.EnablePcapAll(pcap_prefix);

  Simulator::Stop(Seconds(simulation_time));
  Simulator::Run();
  Simulator::Destroy();

  return 0;
}