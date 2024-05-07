import re
import ipaddress


# Validates IP address fromat using regex.
def valid_ip(ip):
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    return re.match(pattern, ip) and all(0 <= int(num) <= 255 for num in ip.split('.'))


# Validates the CIDR format.
def valid_cidr(cidr):
    try:
        return 0 < int(cidr) < 32
    except ValueError:
        return False
    

# Conver the CIDR to subnet mask.
def calculate_subnet_mask(cidr):
    return str(ipaddress.IPv4Network(f'0.0.0.0/{cidr}').netmask)


# Converts the IP class into CIDR.
def cidr_from_ip(ip):
    first_octet = int(ip.split('.')[0])
    if first_octet < 128:
        return 8     # Class A
    elif first_octet < 192:
        return 16    # Class B
    elif first_octet < 224:
        return 24    # Class C
    return 0        # Default for others

# Subnet calculations based on the type of partition and return datailed info.
def subnet_calculations(ip, cidr, partition_type, partitions_num):
    network = ipaddress.IPv4Network(f'{ip}/{cidr}', strict=False)
    if partition_type == 'hosts':
        prefix = 32 - (partitions_num - 1).bit_length()
    elif partition_type == 'subnets':
        prefix = cidr + (partitions_num - 1).bit_length()
    
    networks = []
    try:
        networks = list(network.subnets(new_prefix=prefix))
    except ValueError:
        raise ValueError("Not enough bits to accommodate the specified number of partitions")
    
    if not networks:
        raise ValueError("No subnets calculated.")

    results = {
        "Subnet Mask": calculate_subnet_mask(cidr),
        "CIDR": cidr,
        "Number of Hosts": (2 ** (32 - cidr)) - 2,
        "Number of Subnets": len(networks),
        "Subnets": []
    }

    for net in networks[:2] + networks[-2:]:
        results["Subnets"].append({
            "Network Address": str(net.network_address),
            "Broadcast Address": str(net.broadcast_address)
        })

    return results


# Main function for user interaction.
def main():
    ip = input("Enter a valid ip address: ")
    if not valid_ip(ip):
        print("Invalid IP address.")
        return
    
    cidr = input("Enter CIDR (optional), or press enter to skip: ")
    if cidr:
        if not valid_cidr(cidr):
            print("Invalid CIDR number.")
            return
        cidr = int(cidr)
    # If CIDR was not provided, infer it from IP class.
    else:
        cidr = cidr_from_ip(ip)
        
    partition_type = input("Partition by number of hosts or subnets? Enter 'hosts' or 'subnets': ")
    partition_type = partition_type.lower()
    if partition_type not in ['hosts', 'subnets']:
        print("Invalid partition type.")
        return
    
    partitions_num = input(f"Enter number of {partition_type}: ")
    if not partitions_num.isdigit():
        print("Invalid number.")
        return
    partitions_num = int(partitions_num)

    try:
        results = subnet_calculations(ip, cidr, partition_type, partitions_num)
        print(f"Subnet Mask: {results['Subnet Mask']}")
        print(f"CIDR: {results['CIDR']}")
        print(f"Number of Hosts: {results['Number of Hosts']}")
        print(f"Number of Subnets: {results['Number of Subnets']}")
        for subnet in results['Subnets']:
            print(f"Network Address: {subnet['Network Address']}, Boardcast Address: {subnet['Broadcast Address']}")
    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    main()
