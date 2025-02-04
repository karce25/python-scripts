import csv

def search_ips_in_files(ip_csv, input_files, output_file):
    try:
        # Read IP addresses from the CSV file
        ip_addresses = []
        with open(ip_csv, 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                ip_addresses.extend(row)
        
        # Remove any empty strings from the list
        ip_addresses = [ip.strip() for ip in ip_addresses if ip.strip()]

        with open(output_file, 'w') as outfile:
            for ip_address in ip_addresses:
                for input_file in input_files:
                    try:
                        with open(input_file, 'r') as infile:
                            for line in infile:
                                if ip_address in line:
                                    outfile.write(f"{input_file} - {ip_address}: {line}")
                    except FileNotFoundError:
                        print(f"Error: The file '{input_file}' was not found.")
                    except Exception as e:
                        print(f"An error occurred while reading '{input_file}': {e}")
        print(f"Search complete. Lines containing IP addresses from '{ip_csv}' have been written to '{output_file}'.")
    except FileNotFoundError:
        print(f"Error: The file '{ip_csv}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
ip_csv = 'ip_new.csv'  # Replace with your CSV file containing IP addresses
input_files = ['config_file_1.txt', 'config_file_2.txt', 'config_file_3.txt', 'config_file_4.txt']  # Replace with your input file paths
output_file = 'output.txt'  # Replace with your desired output file path

search_ips_in_files(ip_csv, input_files, output_file)
