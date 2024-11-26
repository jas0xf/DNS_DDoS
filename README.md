# DNS DDoS Amplification Tool

For educational purposes only
## Description

This tool demonstrates how to utilize DNS amplification techniques to increase network traffic as part of a Distributed Denial of Service (DDoS) attack, emphasizing the impact of DNS over UDP.
## How It Works

By leveraging Extended DNS (EDNS), this tool can generate responses up to 1232 bytes from a UDP query that requires only around 100 bytes. According to the 2020 DNS Flag Day standards, most common DNS services—such as DNSMasq, Unbound, PowerDNS, and Bind—support EDNS and are configured to allow this response size by default.

The use of UDP enables easy source IP spoofing, a crucial element in DDoS attacks. Since UDP doesn’t verify the source IP, attackers can direct large volumes of amplified traffic to a target IP.

## Requirements
```bash
pip3 install scapy duckdb
```


## Usage
```bash
python3 CommandProcessor.py [-h] [action] [target]
```
positional arguments:
  action      Action to perform: update, attack(require root privileges)
  target      Target IP for attack or input file for update

options:
  -h, --help  show this help message and exit

1. please retrieve the list of open DNS servers from the FoFa search engine. Query prompt is in ./fofa_prompt file
2. download the json from the result page, just select the ip part to download.
3. update the database, it will check the availability of the DNS server and store the result in ./dns_servers.db
```bash
python3 CommandProcessor.py update {fileName_retrieved_from_FoFa}
```
4. attack the target with the DNS servers in the database
```bash
python CommandProcessor.py attack {target}
# or python CommandProcessor {target}
```


## Key Points

- Port Accessibility: DNS services typically operate on Port 53, which is often open to the public, facilitating ease of access.
- Availability of Open DNS Services: According to FoFa, a popular search engine for internet-connected devices, there are approximately 6 million public DNS services in East Asia alone.
- Amplification Potential: With 100 Mbps of upload bandwidth, an attacker could theoretically initiate a 1 Gbps DDoS attack by exploiting 100,000 open DNS servers.
