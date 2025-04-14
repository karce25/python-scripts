import csv

# Input and output file names
input_file = 'output.txt'
output_file = 'output.csv'

# Initialize storage for rows
rows = []

# Open and read the input file
with open(input_file, 'r') as infile:
    current_ip = ""
    datagroups = []  # List of datagroups where the node is found
    current_pool = ""
    virtual_servers = []  # List of virtual servers
    pools_affected = []  # Pools affected

    for line in infile:
        line = line.strip()

        # Extract Processing IP
        if line.startswith("Processing IP:"):
            current_ip = line.replace("Processing IP: ", "")
            datagroups = []  # Reset datagroups for the new IP
            continue

        # Extract Datagroups where the node IP is found
        elif line.startswith("Datagroup where node is found:"):
            datagroup = line.replace("Datagroup where node is found: ", "")
            datagroups.append(datagroup)

        # Identify Pools Associated
        elif line.startswith("Pools Associated with the IP:"):
            continue
        elif line.startswith("-"):  # Pool line
            current_pool = line.replace("-", "").strip()

        # Extract Virtual Servers
        elif line.startswith("Extracted Virtual servers:"):
            virtual_servers = []  # Reset for new set of virtual servers
        elif line.startswith('"') or line.startswith('/Common'):
            virtual_servers.append(line)

        # Extract Pools Affected
        elif line.startswith("Pools Affected by"):
            pools_affected = []  # Reset for new affected pools
        elif line.startswith("/Common"):  # Affected pool entries
            pools_affected.append(line)

        # Append the row when section ends
        elif line == "=========================================":
            # Add aggregated row to the CSV file
            rows.append([
                current_ip,
                "; ".join(datagroups),
                current_pool,
                "; ".join(virtual_servers),
                "; ".join(pools_affected)
            ])

            # Reset variables for the next section
            current_ip = ""
            datagroups = []
            current_pool = ""
            virtual_servers = []
            pools_affected = []

# Write rows to a CSV file
with open(output_file, 'w', newline='') as outfile:
    writer = csv.writer(outfile)

    # Specify headers for the CSV file
    writer.writerow([
        "Processing IP",
        "Datagroup where node is found",
        "Processing Pool",
        "Extracted Virtual servers",
        "Pools Affected by"
    ])

    # Write the rows collected from the input file
    writer.writerows(rows)

print(f"Data has been successfully extracted to {output_file}")
