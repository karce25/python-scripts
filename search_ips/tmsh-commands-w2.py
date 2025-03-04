#!/usr/bin/env python3
import csv

def generate_tmsh_commands(csv_file, snat_pool, irule, output_file, rollback_file):
    tmsh_commands = []
    rollback_commands = []

    # Add headers for the text files
    tmsh_commands.append("# Generated TMSH and a Bash Command for BIG-IP Configuration")
    rollback_commands.append("# Generated Rollback Bash Commands ")

    # Read the CSV file
    try:
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)

            # Validate the column name
            if 'virtual_server_name' not in reader.fieldnames:
                print("ERROR: CSV file must have a 'virtual_server_name' column.")
                return

            for row in reader:
                vs_name = row['virtual_server_name']
                
                # Generate traditional TMSH modify commands
                tmsh_commands.append(f"# Virtual Server: {vs_name}")
                tmsh_commands.append(f"tmsh modify ltm virtual {vs_name} source-address-translation {{ pool {snat_pool} type snat }}")

                # Add a Bash one-liner to append the iRule dynamically
                bash_command = (
                    f"RULES=$(tmsh list ltm virtual {vs_name} rules | awk '/rules {{/,/}}/ {{if (!/rules {{|}}/) print}}' | tr '\\n' ' '); "
                    f"tmsh modify ltm virtual {vs_name} rules {{ $RULES {irule} }}"
                )
                tmsh_commands.append(f"# Bash command to append the new iRule without replacing existing ones")
                tmsh_commands.append(bash_command)

                # Add rollback bash command to remove the iRule dynamically
                rollback_bash_command = (
                    f"RULES=$(tmsh list ltm virtual {vs_name} rules | awk '/rules {{/,/}}/ {{if (!/rules {{|}}/) print}}' | tr '\\n' ' ' | sed 's/{irule}//g'); "
                    f"tmsh modify ltm virtual {vs_name} rules {{ $RULES }}"
                )
                rollback_commands.append(f"# Rollback for Virtual Server: {vs_name}")
                rollback_commands.append(rollback_bash_command)
                
                # Rollback to restore automap SNAT
                rollback_commands.append(f"tmsh modify ltm virtual {vs_name} source-address-translation {{ type automap }}")

        # Write all commands to the respective files
        with open(output_file, 'w') as file:
            file.write("\n".join(tmsh_commands))

        with open(rollback_file, 'w') as file:
            file.write("\n".join(rollback_commands))

        print(f"TMSH commands have been saved to {output_file}")
        print(f"Rollback commands have been saved to {rollback_file}")

    except FileNotFoundError:
        print(f"ERROR: The file {csv_file} was not found.")
    except KeyError as e:
        print(f"ERROR: Missing expected column in CSV file: {e}")
    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {e}")


# Inputs
csv_file = input("Enter the CSV filename (e.g., virtual_servers.csv): ")
snat_pool = input("Enter the SNAT pool name: ")
irule = input("Enter the iRule name: ")
output_file = input("Enter the output filename for generated commands (default: tmsh_commands.txt): ")
rollback_file = input("Enter the output filename for rollback commands (default: tmsh_rollback_commands.txt): ")

# Use default filenames if none are provided
if not output_file.strip():
    output_file = "tmsh_commands.txt"
if not rollback_file.strip():
    rollback_file = "tmsh_rollback_commands.txt"

# Generate commands
generate_tmsh_commands(csv_file, snat_pool, irule, output_file, rollback_file)
