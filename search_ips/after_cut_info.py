import csv
import re

def parse_csv_file(csv_file):
    """Read the CSV file and return a dictionary mapping pool names to Target IPs."""
    pool_mapping = {}
    with open(csv_file, "r", newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            assigned_pools = row["Assigned pools"].replace(",", "").split()  # Split multiple pools into a list
            target_ip = row["Target IP"]
            for pool in assigned_pools:
                pool_mapping[pool] = target_ip
    return pool_mapping

def parse_text_file(text_file, pool_mapping):
    """Parse the text file to extract pool, IP, and port data."""
    pool_ip_port_mapping = {}
    
    with open(text_file, "r") as file:
        content = file.read()
        for pool, target_ip in pool_mapping.items():
            # Find pool configuration blocks using regex
            pool_pattern = re.compile(rf"#Configuration for pool: {pool}.*?tmsh modify ltm pool {pool} members add .*?{{ (.*?) }}", re.DOTALL)
            match = pool_pattern.search(content)
            if match:
                members = match.group(1).strip()  # Extract members section
                # Extract all port numbers from the 'members' section
                ports = re.findall(r":(\d+)", members)
                pool_ip_port_mapping[target_ip] = pool_ip_port_mapping.get(target_ip, []) + ports
    return pool_ip_port_mapping

def write_to_csv(output_file, pool_ip_port_mapping):
    """Write the pool and port mappings to a new CSV file."""
    with open(output_file, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Pool", "Port"])  # Header row
        for pool, ports in pool_ip_port_mapping.items():
            writer.writerow([pool, ", ".join(sorted(set(ports)))])  # Pool IP and unique, sorted ports

def main():
    # Specify file paths
    csv_file = "input.csv"  # Update this to the path of your input CSV file
    text_file = "input.txt"  # Update this to the path of your input text file
    output_file = "output.csv"  # Desired output file path

    # Process files
    pool_mapping = parse_csv_file(csv_file)
    pool_ip_port_mapping = parse_text_file(text_file, pool_mapping)
    write_to_csv(output_file, pool_ip_port_mapping)

    print(f"Output written to {output_file}")

if __name__ == "__main__":
    main()
