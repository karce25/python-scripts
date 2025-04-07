import csv
from collections import deque

def search_ips_in_files(ip_csv, input_files):
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
                match_content = []  # Store the matched content
                
                with open(input_file, 'r') as infile:
                    previous_lines = deque(maxlen=5)
                    lines_after_match = 0
                    after_match_buffer = []

                    for line in infile:
                        if lines_after_match > 0:  # Collect lines after match
                            after_match_buffer.append(line.strip())
                            lines_after_match -= 1
                            if lines_after_match == 0:
                                match_content.append("-- Context Before Match --\n")
                                match_content.append("\n".join(previous_lines) + "\n")
                                match_content.append("-- MATCH FOUND --\n")
                                match_content.append("\n".join(after_match_buffer) + "\n")
                                match_content.append("\n" + "-" * 40 + "\n")
                                previous_lines.clear()
                                after_match_buffer = []
                            continue

                        previous_lines.append(line.strip())
                        for ip_address in ip_addresses:
                            if ip_address in line:
                                found_matches = True
                                unmatched_ips.discard(ip_address)  # Mark the IP as matched
                                lines_after_match = 6  # Start collecting lines after the match
                                after_match_buffer.append(line.strip())
                                break  # Stop checking other IPs for this line

                if found_matches:
                    # Write matched content to an output file specific to the text file
                    output_file = f"{input_file}_output.txt"
                    with open(output_file, 'w') as outfile:
                        outfile.writelines(match_content)
                    print(f"Matches for IP addresses found in '{input_file}', written to '{output_file}'.")
                else:
                    print(f"No matches for IP addresses were found in '{input_file}'.")
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
search_ips_in_files(ip_csv, input_files)  # Output files created in the current directory
