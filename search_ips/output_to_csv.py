import csv

# Input and output filenames
input_file = 'output.txt'
csv_file = 'output_v2.csv'

# Initialize storage for rows
rows = []
virtual_servers_collected = False  # Flag for tracking Extracted Virtual servers

# Open and read the input file
with open(input_file, 'r') as infile:
    # Initialize variables for each section
    current_ip = ""  # Current IP
    datagroups = []  # Datagroups where the node is found
    current_pool = ""  # Processing Pool
    virtual_servers = []  # Extracted Virtual servers for the current pool
    pools_affected = []  # Pools Affected for the current pool
    virtual_server_attached = ""  # Virtual Server Attached to the current pool

    for line in infile:
        line = line.strip()

        # Extract Processing IP
        if line.startswith("Processing IP:"):
            # Store the completed row for the previous section (if any exists)
            if current_ip and current_pool:
                rows.append([
                    current_ip,
                    "; ".join(datagroups),  # Combine datagroups into one column
                    current_pool,
                    "; ".join(virtual_servers),  # Combine virtual servers into one column
                    "; ".join(pools_affected),  # Combine pools affected into one column
                    virtual_server_attached  # Virtual Server Attached
                ])

            # Start a new section; reset all relevant fields
            current_ip = line.replace("Processing IP: ", "").strip()
            datagroups = []  # Reset datagroups for the new IP section
            current_pool = ""  # Reset processing pool
            virtual_servers = []  # Reset virtual servers list
            pools_affected = []  # Reset pools affected list
            virtual_server_attached = ""  # Reset virtual server attached
            continue

        # Extract Datagroup where node is found
        elif line.startswith("Datagroup where node is found:"):
            datagroup = line.replace("Datagroup where node is found: ", "").strip()
            datagroups.append(datagroup)

        # Extract "Processing Pool"
        elif line.startswith("Processing Pool:"):
            # If we are moving to a new pool, store the previous pool's data first
            if current_pool:
                rows.append([
                    current_ip,
                    "; ".join(datagroups),
                    current_pool,
                    "; ".join(virtual_servers),
                    "; ".join(pools_affected),
                    virtual_server_attached
                ])
            
            # Update to the new pool and reset related variables
            current_pool = line.replace("Processing Pool: ", "").strip()
            virtual_servers = []  # Reset virtual servers for the new pool
            pools_affected = []  # Reset pools affected for the new pool
            virtual_server_attached = ""  # Reset virtual server attached for the new pool

        # Start capturing Virtual Servers after "Extracted Virtual servers:"
        elif line.startswith("Extracted Virtual servers:"):
            virtual_servers_collected = True
            virtual_servers = []  # Reset virtual servers list

        elif virtual_servers_collected:
            # Stop capturing when Extended Search begins
            if line.startswith("Performing Extended Search"):
                virtual_servers_collected = False
            elif line.startswith('/Common') or line.startswith('"'):  # Virtual server entry
                virtual_servers.append(line.strip())

        # Extract "Pools Affected"
        elif line.startswith("Pools Affected by"):
            pools_affected = []  # Reset pools affected for the current pool
        elif line.startswith("/Common"):  # Pools affected entries
            pools_affected.append(line.strip())

        # Extract "Virtual Server Attached to"
        elif line.startswith("Virtual Server Attached to"):
            # Extract the virtual server attached for the current pool
            virtual_server_attached = line.split(": ")[1].strip()

        # End of a section or processing block
        elif line == "=========================================":
            # Append the completed section to the rows
            if current_ip and current_pool:
                rows.append([
                    current_ip,
                    "; ".join(datagroups),
                    current_pool,
                    "; ".join(virtual_servers),
                    "; ".join(pools_affected),
                    virtual_server_attached
                ])

            # Reset variables for the next section
            current_pool = ""
            virtual_servers = []
            pools_affected = []
            virtual_server_attached = ""

# Write rows to a CSV file
with open(csv_file, 'w', newline='') as outfile:
    writer = csv.writer(outfile)

    # Add headers to the CSV file
    writer.writerow([
        "Node_IP",
        "Datagroup where node is found",
        "Pool where node is found",
        "Virtual servers from datagroups",
        "Pools Affected by virtual server datagroups ",
        "Virtual server"
    ])

    # Write the extracted rows to the CSV
    writer.writerows(rows)

print(f"Data successfully exported to {csv_file}")
