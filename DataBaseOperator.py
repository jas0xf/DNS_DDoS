import duckdb
import json
from typing import List

from ValidationProcessor import DNSValidator


class DNSDatabaseManager:
    def __init__(self, db_path: str = 'dns_servers.db'):
        """
        Initialize the Database Manager
        
        :param db_path: Path to the DuckDB database file
        """
        self.db_path = db_path
        self.conn = duckdb.connect(db_path)
        self._create_tables()
        self.validator = DNSValidator()

    def _create_tables(self):
        """
        Create necessary tables in the database
        """
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS dns_servers (
                host VARCHAR PRIMARY KEY,
                ip VARCHAR,
                is_valid BOOLEAN,
                is_responsive BOOLEAN,
                last_check_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_checks INTEGER DEFAULT 0,
                successful_checks INTEGER DEFAULT 0
            )
        ''')

    def get_all_dns_servers(self) -> List[str]:
        """
        Retrieve all DNS server IPs from the database
        
        :return: List of DNS server IPs
        """
        return [
            row[0] for row in 
            self.conn.execute('SELECT ip FROM dns_servers').fetchall()
        ]

    def validate_and_update_dns_servers(self, 
                                        validate: bool = True, 
                                        min_success_rate: float = 0.8) -> List[dict]:
        """
        Comprehensive validation of DNS servers using DNSValidator
        
        :param validate: Whether to perform validation
        :param min_success_rate: Minimum success rate to keep a DNS server
        :return: List of validated DNS server details
        """
        if not validate:
            return []

        servers = self.conn.execute('SELECT ip FROM dns_servers').fetchall()
        ips = [server[0] for server in servers]
        
        successful_ips = self.validator.validate_ips(ips)
        
        validation_results = []
        for ip in ips:
            is_successful = ip in successful_ips
            
            current_stats = self.conn.execute(
                'SELECT total_checks, successful_checks FROM dns_servers WHERE ip = ?', 
                (ip,)
            ).fetchone()
            
            total_checks = (current_stats[0] if current_stats else 0) + 1
            successful_checks = (current_stats[1] if current_stats else 0) + (1 if is_successful else 0)
            
            success_rate = successful_checks / total_checks if total_checks > 0 else 0
            
            keep_server = success_rate >= min_success_rate
            
            if keep_server:
                self.conn.execute('''
                    UPDATE dns_servers 
                    SET 
                        is_valid = ?, 
                        is_responsive = ?, 
                        last_check_timestamp = CURRENT_TIMESTAMP,
                        total_checks = ?,
                        successful_checks = ?
                    WHERE ip = ?
                ''', (
                    is_successful, 
                    is_successful, 
                    total_checks, 
                    successful_checks, 
                    ip
                ))
            else:
                self.conn.execute('DELETE FROM dns_servers WHERE ip = ?', (ip,))
            
            validation_results.append({
                'ip': ip,
                'is_valid': is_successful,
                'is_responsive': is_successful,
                'total_checks': total_checks,
                'successful_checks': successful_checks,
                'success_rate': success_rate,
                'kept': keep_server
            })
        
        # Log validation summary
        total_servers = len(ips)
        valid_servers = len([r for r in validation_results if r['kept']])
        
        print(f"\nDNS Server Validation Summary:")
        print(f"Total Servers Checked: {total_servers}")
        print(f"Valid Servers Retained: {valid_servers}")
        print(f"Retention Rate: {valid_servers/total_servers*100:.2f}%")
        
        return validation_results

    def insert_from_json_file(self, json_file_path: str):
        """
        Insert DNS servers from a Fofa JSON file
        
        :param json_file_path: Path to the JSON file
        """
        try:
            with open(json_file_path, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        # Extract IP from host if needed
                        ip = entry.get('ip') or entry.get('host', '').split(':')[0]
                        
                        # Initial insertion with default validation status
                        self.conn.execute('''
                            INSERT OR REPLACE INTO dns_servers 
                            (host, ip, is_valid, is_responsive, total_checks, successful_checks) 
                            VALUES (?, ?, NULL, NULL, 0, 0)
                        ''', (entry.get('host', ip), ip))
                    except json.JSONDecodeError:
                        print(f"Skipping invalid JSON line: {line}")
                    except Exception as e:
                        print(f"Error processing entry: {e}")
        except FileNotFoundError:
            print(f"File not found: {json_file_path}")

    def convert_to_json(self, input_file, output_file):
        """
        Convert a text file with IPs to a JSON file with host:port format
        
        :param input_file: Path to input text file with IPs
        :param output_file: Path to output JSON file
        """
        with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
            for line in infile:
                ip = line.strip()
                # Create JSON entry with host:port format (default DNS port 53)
                entry = {
                    "host": f"{ip}:53",
                    "ip": ip
                }
                # Write each JSON object on a new line
                json.dump(entry, outfile)
                outfile.write('\n')



def main():
    db_manager = DNSDatabaseManager()
    
    db_manager.convert_to_json('dns_servers.txt', 'dns_servers.json')
    db_manager.insert_from_json_file('dns_servers.json')
    
    validation_results = db_manager.validate_and_update_dns_servers(
        validate=True,
        min_success_rate=0.8
    )
    
    print("\nDetailed Validation Results:")
    for result in validation_results:
        print(f"IP: {result['ip']}")
        print(f"  Valid: {result['is_valid']}")
        print(f"  Total Checks: {result['total_checks']}")
        print(f"  Successful Checks: {result['successful_checks']}")
        print(f"  Success Rate: {result['success_rate']:.2%}")
        print(f"  Kept in Database: {result['kept']}\n")

if __name__ == "__main__":
    # main()
    db_manager = DNSDatabaseManager()
    print(db_manager.get_all_dns_servers())
    



