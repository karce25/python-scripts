import csv

def generate_egrep_commands(ip_csv_file, output_file="egrep_commands.txt"):
    """
    Generate egrep commands for IP addresses from a CSV file and save them into a TXT file.

    :param ip_csv_file: Path to the CSV file containing IP addresses
    :param output_file: Output text file to save the commands
    """
    try:
        # Open the CSV file
        with open(ip_csv_file, mode='r') as csvfile:
            reader = csv.reader(csvfile)
            ip_addresses = [row[0] for row in reader if row]  # Read IP addresses from the first column

        # Generate and save egrep commands for each IP
        with open(output_file, mode='w') as outfile:
            for ip in ip_addresses:
                egrep_command = f"egrep  {ip} bigip.conf"
                outfile.write(egrep_command + "\n")  # Write each command as a separate line
        
        print(f"Commands generated and saved to {output_file}")

    except FileNotFoundError:
        print(f"Error: The file {ip_csv_file} was not found. Please provide a valid file.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Usage example
input_csv = "ips.csv"  # Replace with the path to your CSV file
generate_egrep_commands(input_csv)
