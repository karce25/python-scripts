import csv

def search_exact_ips_in_bigip_multiple(ip_csv, input_files):
    try:
        # Read IP addresses from the CSV file and validate input
        with open(ip_csv, 'r') as csvfile:
            reader = csv.reader(csvfile)
            ip_addresses = set(ip.strip() for row in reader for ip in row if ip.strip())  # Use a set for faster lookups
        if not ip_addresses:
            print("Error: The CSV file is empty or contains no valid IP addresses.")
            return

        # Track unmatched IPs
        unmatched_ips = ip_addresses.copy()

        for input_file in input_files:
            try:
                matched_ips = set()  # To store the IPs matched in this file

                # Read and process the current bigip.conf file
                with open(input_file, 'r') as infile:
                    for line in infile:
                        # Tokenize the line into individual words separated by spaces or non-word characters
                        tokens = line.split()  # Split based on whitespace
                        for ip_address in ip_addresses:
                            # Perform exact matching (check if IP exists as a whole token)
                            if ip_address in tokens:  # Ensure exact match
                                matched_ips.add(ip_address)  # Track matched IP
                                unmatched_ips.discard(ip_address)  # Mark IP as matched
                                break  # Break once a match is found for this line

                # Handle matched IPs output for the current file
                if matched_ips:
                    output_file = f"{input_file}_output.txt"
                    with open(output_file, 'w') as outfile:
                        outfile.write("\n".join(matched_ips))
                    print(f"Exact matches for IP addresses found in '{input_file}', written to '{output_file}'.")
                else:
                    print(f"No exact matches for IP addresses were found in '{input_file}'.")

            except FileNotFoundError:
                print(f"Error: The file '{input_file}' was not found.")
            except Exception as e:
                print(f"An error occurred while reading '{input_file}': {e.__class__.__name__}: {e}")

        # Handle unmatched IPs output for all processed files
        unmatched_ips_file = "unmatched_ips.txt"
        with open(unmatched_ips_file, 'w') as unmatched_file:
            unmatched_file.write("\n".join(unmatched_ips))
        print(f"Unmatched IP addresses written to: {unmatched_ips_file}")

    except FileNotFoundError:
        print(f"Error: The file '{ip_csv}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e.__class__.__name__}: {e}")

# Example usage
ip_csv = 'ip_new.csv'  # Replace with your CSV file containing IP addresses
input_files = ['bigip1.conf', 'bigip2.conf', 'bigip3.conf', 'bigip4.conf']  # Replace with paths to your BigIP configuration files
search_exact_ips_in_bigip_multiple(ip_csv, input_files)  # Outputs files in the current directory
