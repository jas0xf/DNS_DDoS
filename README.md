# DNS DDoS
**This is a tool for educational purpose**
***

## Description
Using the mechanism of Extended DNS, we can get *1232 bytes of response with UDP query within 100 bytes.
*1232 bytes is suggested by 2020 DNS flag day. Thus all common DNS services, such as DNSMasq, Unbound, PowerDNS, Bind, etc, set it as default.

the feature of UDP makes it easy to spoof the source IP address, which is the key to DDoS attack.

Port 53 are usually open for DNS service, so it can be launched easily.
Tons of DNS services are opened to the public, according to FoFa search engine, there are 6 million DNS services opened to the public in East Asia.

Theoretically, we can launch 1 GBps attack with 100 MBps upload bandwidth via 100k DNS services.


# DNS DDoS Amplification Tool

For educational purposes only
## Description

This tool demonstrates how to utilize DNS amplification techniques to increase network traffic as part of a Distributed Denial of Service (DDoS) attack, emphasizing the impact of DNS over UDP.
## How It Works

By leveraging Extended DNS (EDNS), this tool can generate responses up to 1232 bytes from a UDP query that requires only around 100 bytes. According to the 2020 DNS Flag Day standards, most common DNS services—such as DNSMasq, Unbound, PowerDNS, and Bind—support EDNS and are configured to allow this response size by default.

The use of UDP enables easy source IP spoofing, a crucial element in DDoS attacks. Since UDP doesn’t verify the source IP, attackers can direct large volumes of amplified traffic to a target IP.
## Key Points

    Port Accessibility: DNS services typically operate on Port 53, which is often open to the public, facilitating ease of access.
    Availability of Open DNS Services: According to FoFa, a popular search engine for internet-connected devices, there are approximately 6 million public DNS services in East Asia alone.
    Amplification Potential: With 100 Mbps of upload bandwidth, an attacker could theoretically initiate a 1 Gbps DDoS attack by exploiting 100,000 open DNS servers.
