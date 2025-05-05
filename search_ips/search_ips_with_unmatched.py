import csv

def search_exact_ips_in_files(ip_csv, input_files):
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
                found_matches = False  # Flag to check if any matches are found
                matched_ips = set()  # Store matched IPs for the current file

                with open(input_file, 'r') as infile:
                    for line in infile:
                        # Check if the line contains an exact match (whole word match)
                        # Match each IP against individual line
                        for ip_address in ip_addresses:
                            # Perform exact match by ensuring the IP is surrounded by non-word characters
                            tokens = line.split()  # Split line into tokens
                            if ip_address in tokens:  # Check for exact match of IP as a token
                                found_matches = True
                                matched_ips.add(ip_address)  # Track the matched IP
                                unmatched_ips.discard(ip_address)  # Mark the IP as matched
                                break  # Stop checking other IPs for this line

                # Write matched IPs directly to an output file specific to the text file
                if found_matches:
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

        # Write unmatched IP addresses to a separate file (current directory)
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
input_files = ['config_file_1.txt', 'config_file_2.txt', 'config_file_3.txt', 'config_file_4.txt']  # Replace with input file paths
search_exact_ips_in_files(ip_csv, input_files)  # Output files created in the current directory
