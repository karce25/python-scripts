import csv

# Input and output filenames
input_file = 'output.txt'
output_file = 'output.csv'

# Initialize storage for rows
rows = []

# Read and parse data from output.txt
with open(input_file, 'r') as infile:
    current_ip = ""
    datagroup = ""
    pools = ""
    virtual_server = ""
    pools_affected = []
    for line in infile:
        line = line.strip()

        # Process IP Address
        if line.startswith("Processing IP:"):
            current_ip = line.replace("Processing IP: ", "")

        # Process Datagroup Name
        elif line.startswith("Datagroup where node is found:"):
            datagroup = line.replace("Datagroup where node is found: ", "")

        # Process Pools Associated with IP
        elif line.startswith("Pools Associated with the IP:"):
            pools = next(infile).strip()  # Get the next line after Pools Associated

        # Process Virtual Server Name
        elif line.startswith("Virtual Server Attached to"):
            virtual_server = line.split(": ")[1] if ": " in line else ""

        # Process Pools Affected
        elif line.startswith("Pools Affected by"):
            if ": " in line:  # Validate proper formatting
                pools_affected.append(line.split(": ")[1].strip())

        # Section End Marker
        elif line == "=========================================":
            # Append row and reset variables at section end
            rows.append([current_ip, datagroup, pools, virtual_server, "; ".join(pools_affected)])
            current_ip = datagroup = pools = virtual_server = ""
            pools_affected = []

# Write data to a CSV file
with open(output_file, 'w', newline='') as outfile:
    writer = csv.writer(outfile)
    # Add header row
    writer.writerow(["IP", "Datagroup", "Pools", "Virtual Server", "Pools Affected"])
    # Add all rows
    writer.writerows(rows)

print(f"Data has been written to {output_file}")
