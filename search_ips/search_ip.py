import csv
from collections import deque

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
                            # Use a deque to buffer previous 5 lines
                            previous_lines = deque(maxlen=5)
                            lines_after_match = 0
                            after_match_buffer = []

                            for line_number, line in enumerate(infile):
                                if lines_after_match > 0:  # Keep appending lines after a match is found
                                    after_match_buffer.append(line.strip())
                                    lines_after_match -= 1
                                    if lines_after_match == 0:
                                        # Write buffered context (5 lines before, match, and 5 after)
                                        outfile.write(f"\nFile: {input_file} (Match for '{ip_address}')\n")
                                        outfile.write("\n".join(previous_lines) + "\n")
                                        outfile.write("-- MATCH --\n")
                                        outfile.write("\n".join(after_match_buffer) + "\n")
                                        outfile.write("\n" + "-" * 40 + "\n")
                                        # Reset buffers for the next match
                                        previous_lines.clear()
                                        after_match_buffer = []
                                    continue

                                previous_lines.append(line.strip())  # Buffer the last 5 lines
                                if ip_address in line:
                                    # Start collecting lines after the match
                                    lines_after_match = 6  # 5 + the matched line
                                    after_match_buffer.append(line.strip())  # Match itself
                                    
                    except FileNotFoundError:
                        print(f"Error: The file '{input_file}' was not found.")
                    except Exception as e:
                        print(f"An error occurred while reading '{input_file}': {e}")
        print(f"Search complete. Contextual matches from '{ip_csv}' have been written to '{output_file}'.")
    except FileNotFoundError:
        print(f"Error: The file '{ip_csv}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
ip_csv = 'ip_new.csv'  # Replace with your CSV file containing IP addresses
input_files = ['config_file_1.txt', 'config_file_2.txt', 'config_file_3.txt', 'config_file_4.txt']  # Replace with your input file paths
output_file = 'output.txt'  # Replace with your desired output file path
search_ips_in_files(ip_csv, input_files, output_file)
