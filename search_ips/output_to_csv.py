import csv

# Input and output filenames
input_file = 'output.txt'
csv_file = 'output.csv'

# Initialize storage for rows
rows = []
virtual_servers_collected = False  # Flag for tracking Extracted Virtual servers

# Open and read the input file
with open(input_file, 'r') as infile:
    # Initialize variables for each section
    current_ip = ""
    datagroups = []  # Datagroups where the node is found
    current_pool = ""  # Processing Pool
    virtual_servers = []  # Extracted Virtual servers for the current pool
    pools_affected = []  # Pools Affected for the current pool

    for line in infile:
        line = line.strip()

        # Extract Processing IP
        if line.startswith("Processing IP:"):
            # Store the completed row for the previous section (if any exists)
            if current_ip and current_pool:
                rows.append([
                    current_ip,
                    "; ".join(datagroups),  # Datagroups where the node is found
                    current_pool,
                    "; ".join(virtual_servers),  # Extracted Virtual servers
                    "; ".join(pools_affected)  # Pools Affected
                ])

            # Start a new section; reset all relevant fields
            current_ip = line.replace("Processing IP: ", "").strip()
            datagroups = []  # Reset datagroups for the new IP section
            current_pool = ""  # Reset processing pool
            virtual_servers = []  # Reset virtual servers
            pools_affected = []  # Reset pools affected
            continue

        # Extract Datagroup where node is found
        elif line.startswith("Datagroup where node is found:"):
            datagroup = line.replace("Datagroup where node is found: ", "").strip()
            datagroups.append(datagroup)

        # Process each Processing Pool
        elif line.startswith("Processing Pool:"):
            # If we are moving to a new pool, store the previous pool's data first
            if current_pool:
                rows.append([
                    current_ip,
                    "; ".join(datagroups),  # Datagroups
                    current_pool,
                    "; ".join(virtual_servers),  # Virtual servers
                    "; ".join(pools_affected)  # Pools Affected
                ])
            
            # Update the current pool, reset virtual servers and pools affected
            current_pool = line.replace("Processing Pool: ", "").strip()
            virtual_servers = []  # Reset virtual servers for new pool
            pools_affected = []  # Reset pools affected for new pool

        # Start capturing Virtual Servers after "Extracted Virtual servers:"
        elif line.startswith("Extracted Virtual servers:"):
            virtual_servers_collected = True  # Start collecting virtual servers
            virtual_servers = []  # Reset virtual servers for the pool

        elif virtual_servers_collected:
            # Stop capturing when "Performing Extended Search" begins
            if line.startswith("Performing Extended Search"):
                virtual_servers_collected = False
            elif line.startswith('/Common') or line.startswith('"'):  # Virtual server entry
                virtual_servers.append(line.strip())

        # Extract Pools Affected
        elif line.startswith("Pools Affected by"):
            pools_affected = []  # Start collecting pools affected
        elif line.startswith("/Common"):  # Pools affected entries
            pools_affected.append(line.strip())

        # End of a section or output
        elif line == "=========================================":
            # Add every completed section to rows during each "=========================================" marker
            if current_ip and current_pool:
                rows.append([
                    current_ip,
                    "; ".join(datagroups),  # Datagroups
                    current_pool,
                    "; ".join(virtual_servers),  # Virtual servers
                    "; ".join(pools_affected)  # Pools Affected
                ])

            # Reset fields for processing the next section
            current_pool = ""
            virtual_servers = []
            pools_affected = []

# Write rows to a CSV file
with open(csv_file, 'w', newline='') as outfile:
    writer = csv.writer(outfile)

    # Add headers for the CSV file
    writer.writerow([
        "Processing IP",
        "Datagroup where node is found",
        "Processing Pool",
        "Extracted Virtual servers",
        "Pools Affected by"
    ])

    # Write extracted rows to the CSV
    writer.writerows(rows)

print(f"Data successfully exported to {csv_file}")
