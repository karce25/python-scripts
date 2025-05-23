import csv

# Input and output filenames
input_file = 'output.txt'
csv_file = 'output_v5.csv'

# Initialize storage for rows
rows = []
virtual_servers_collected = False  # Flag for Extracted Virtual servers

# Open and read the input file
with open(input_file, 'r') as infile:
    # Initialize variables for each section
    current_ip = ""  # Node IP (Processing IP)
    datagroups = []  # Datagroups where the node is found
    current_pool = ""  # Processing Pool
    virtual_servers = []  # Extracted Virtual servers for a given pool
    pools_affected = []  # Pools Affected (aggregate within a single pool)
    datagroup_matched = []  # Datagroup matched before the specified line
    virtual_server_attached = ""  # Aggregated Virtual Server Attached to a given pool
    capturing_datagroups = False  # Flag to control when datagroup matching is collected
    capturing_virtual_server_attached = False  # Flag for handling multi-line Virtual Server Attached

    for line in infile:
        line = line.strip()

        # Extract Processing IP
        if line.startswith("Processing IP:"):
            # Store the completed row for the previous section
            if current_ip and current_pool:
                rows.append([
                    current_ip,
                    "; ".join(datagroups),
                    current_pool,
                    "; ".join(virtual_servers),
                    "; ".join(set(pools_affected)),  # Deduplicate pools affected
                    "; ".join(set(datagroup_matched)),  # Deduplicate datagroup matched
                    virtual_server_attached
                ])
            # Start a new section; reset all relevant fields
            current_ip = line.replace("Processing IP: ", "").strip()
            datagroups, virtual_servers, pools_affected, datagroup_matched = [], [], [], []
            current_pool, virtual_server_attached = "", ""
            capturing_datagroups = True  # Allow datagroup matching collection
            capturing_virtual_server_attached = False
            continue

        # Extract Datagroup where node is found
        elif line.startswith("Datagroup where node is found:"):
            datagroups.append(line.replace("Datagroup where node is found: ", "").strip())

        # Extract Processing Pool
        elif line.startswith("Processing Pool:"):
            # Store the previous pool's data if transitioning to a new pool
            if current_pool:
                rows.append([
                    current_ip,
                    "; ".join(datagroups),
                    current_pool,
                    "; ".join(virtual_servers),
                    "; ".join(set(pools_affected)),  # Deduplicate pools affected
                    "; ".join(set(datagroup_matched)),  # Deduplicate datagroup matched
                    virtual_server_attached
                ])
            # Start a new pool; reset related variables
            current_pool = line.replace("Processing Pool: ", "").strip()
            virtual_servers, pools_affected, datagroup_matched = [], [], []  # Reset lists
            virtual_server_attached = ""
            capturing_datagroups = True  # Allow datagroup matching collection again
            capturing_virtual_server_attached = False
            continue

        # Add datagroups matched by pool (only before the "Extracting First Parts" line)
        elif line.startswith("Found in Datagroup:") and capturing_datagroups:
            datagroup = line.replace("Found in Datagroup: ", "").strip()
            datagroup_matched.append(datagroup)

        # Stop capturing datagroup matched when "Extracting First Parts" is encountered
        elif line.startswith("Extracting First Parts of Matching Records..."):
            capturing_datagroups = False  # Stop collecting datagroup matched
            continue

        # Reset everything after the separator (`-----------------------------------------`)
        elif line.startswith("-----------------------------------------"):
            # Append the current pool's data if available
            if current_ip and current_pool:
                rows.append([
                    current_ip,
                    "; ".join(datagroups),
                    current_pool,
                    "; ".join(virtual_servers),
                    "; ".join(set(pools_affected)),  # Deduplicate pools affected
                    "; ".join(set(datagroup_matched)),  # Deduplicate datagroup matched
                    virtual_server_attached
                ])
            # Reset relevant variables for the next section
            current_pool, virtual_servers, pools_affected, datagroup_matched = "", [], [], []
            virtual_server_attached, capturing_virtual_server_attached = "", False
            capturing_datagroups = True  # Reset capturing flag for next pool
            continue

        # Process Virtual Server Attached to (multi-line handling)
        elif line.startswith("Virtual Server Attached to"):
            virtual_server_attached = line.split(": ")[1].strip()
            capturing_virtual_server_attached = True
            continue

        # If capturing multi-line Virtual Servers Attached
        if capturing_virtual_server_attached:
            if line == "" or line.startswith("Processing IP") or line.startswith("Datagroup") or line.startswith("Extracted Virtual servers") or line.startswith("Pools Affected"):
                capturing_virtual_server_attached = False  # Stop capturing
            else:
                virtual_server_attached += " " + line.strip()
                continue

        # Extract Virtual Servers
        elif line.startswith("Extracted Virtual servers:"):
            virtual_servers_collected = True
            virtual_servers = []  # Reset list for virtual servers
            continue

        elif virtual_servers_collected:
            # Stop capturing virtual servers when Extended Search begins
            if line.startswith("Performing Extended Search"):
                virtual_servers_collected = False
            elif line.startswith('/Common') or line.startswith('"'):  # Valid virtual server entry
                virtual_servers.append(line.strip())
            continue

        # Pools Affected processing
        elif line.startswith("Pools Affected by"):
            continue
        elif line.startswith("/Common"):
            pools_affected.append(line.strip())

        # End of a section
        elif line == "=========================================":
            if current_ip and current_pool:
                rows.append([
                    current_ip,
                    "; ".join(datagroups),
                    current_pool,
                    "; ".join(virtual_servers),
                    "; ".join(set(pools_affected)),  # Deduplicate pools affected
                    "; ".join(set(datagroup_matched)),  # Deduplicate datagroup matched
                    virtual_server_attached
                ])
            current_pool, virtual_servers, pools_affected, datagroup_matched = "", [], [], []
            virtual_server_attached = ""
            capturing_datagroups = True  # Reset capturing flag for next pool
            capturing_virtual_server_attached = False

    # Store the last section after finishing the loop
    if current_ip and current_pool:
        rows.append([
            current_ip,
            "; ".join(datagroups),
            current_pool,
            "; ".join(virtual_servers),
            "; ".join(set(pools_affected)),  # Deduplicate pools affected
            "; ".join(set(datagroup_matched)),  # Deduplicate datagroup matched
            virtual_server_attached
        ])

# Write rows to a CSV file
with open(csv_file, 'w', newline='') as outfile:
    writer = csv.writer(outfile)
    # Add headers to the CSV file
    writer.writerow([
        "Node_IP",
        "Datagroup where node is found",
        "Pool where node is found",
        "Virtual servers from datagroups",
        "Pools Affected by virtual server datagroups",
        "Datagroup matched by pool",  # New column for Datagroup Matched by Pool
        "Virtual server"
    ])
    # Write the extracted rows to the CSV
    writer.writerows(rows)

print(f"Data successfully exported to {csv_file}")
