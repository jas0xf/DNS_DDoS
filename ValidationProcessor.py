import subprocess
import ipaddress
import concurrent.futures
from typing import List, Optional
import os
import tempfile
import logging

class DNSValidator:
    def __init__(self, 
                 target_domain: str = "dospayload.chickenkiller.com", 
                 timeout: int = 10,
                 log_level: int = logging.INFO):
        """
        Initialize DNS Validator
        
        :param target_domain: Domain to test DNS resolution
        :param timeout: Timeout for DNS queries in seconds
        :param log_level: Logging level
        """
        self.target_domain = target_domain
        self.timeout = timeout
        
        logging.basicConfig(
            level=log_level, 
            format='%(asctime)s - %(levelname)s: %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def check_ip(self, ip: str) -> bool:
        """
        Check if a DNS server responds correctly
        
        :param ip: IP address to test
        :return: Boolean indicating successful DNS resolution
        """
        try:
            ipaddress.ip_address(ip)
            
            dig_command = [
                'dig', 
                '@' + ip, 
                self.target_domain, 
                'TXT', 
                '+timeout=' + str(self.timeout)
            ]
            
            result = subprocess.run(
                dig_command, 
                capture_output=True, 
                text=True, 
                timeout=self.timeout
            )

            
            if result.returncode == 0:
                if "status: NOERROR" in result.stdout:
                    self.logger.info(f"{ip} succeeded.")
                    return True
                else:
                    self.logger.warning(f"{ip} failed: No error response")
            else:
                self.logger.warning(f"{ip} failed: Dig command error")
            
            return False
        
        except (ipaddress.AddressValueError, subprocess.TimeoutExpired) as e:
            self.logger.error(f"Error checking {ip}: {e}")
            return False

    def validate_ips(self, 
                     ips: List[str], 
                     max_workers: Optional[int] = None,
                     output_file: Optional[str] = None) -> List[str]:
        """
        Validate multiple IPs concurrently
        
        :param ips: List of IP addresses to validate
        :param max_workers: Number of concurrent threads
        :param output_file: Optional file to write successful IPs
        :return: List of valid IP addresses
        """
        if max_workers is None:
            max_workers = min(32, len(ips))
        
        temp_output = output_file or os.path.join(
            tempfile.gettempdir(), 
            'successful_dns_servers.txt'
        )
        
        successful_ips = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_ip = {
                executor.submit(self.check_ip, ip): ip 
                for ip in ips
            }
            
            for future in concurrent.futures.as_completed(future_to_ip):
                ip = future_to_ip[future]
                try:
                    if future.result():
                        successful_ips.append(ip)
                except Exception as e:
                    self.logger.error(f"Unexpected error validating {ip}: {e}")
        
        with open(temp_output, 'w') as f:
            for ip in successful_ips:
                f.write(f"{ip}\n")
        
        self.logger.info(f"Validation complete. {len(successful_ips)} IPs succeeded.")
        self.logger.info(f"Successful IPs written to {temp_output}")
        
        return successful_ips

def main():
    validator = DNSValidator()
    # single_result = validator.check_ip('8.8.8.8')
    # print(f"Single IP check result: {single_result}")
    
    test_ips = [
        '8.8.8.8',     # Google DNS
        '1.1.1.1',     # Cloudflare DNS
        '9.9.9.9',     # Quad9 DNS
        '208.67.222.222'  # OpenDNS
    ]
    
    valid_ips = validator.validate_ips(test_ips)
    print("Valid IPs:", valid_ips)

if __name__ == "__main__":
    main()
