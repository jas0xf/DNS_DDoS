# Service
- Dnsmasq => edns-max-size = 1232 (ipv4 1280, ipv6 include header so it's default 1232)
- Unbound => edns-buffer-size = 1232
- PowerDNS => edns-outgoing-bufsize = 1232
- Bind => edns-udp-size = 1232
- CoreDNS => bufsize = 1232
- Cisco Network Registrar => edns-max-payload = 1232
- Knot Resolver => udp-max-payload = 1232
- Microsoft DNS => EDNS buffer = 1232
- NSD => ipv4-edns-size = 1232

# DNS
- FreeDSN: http://freedns.afraid.org/subdomain/edit.php?edit_domain_id=14
- domain: dospayload.chickenkiller.com
