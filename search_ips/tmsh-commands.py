#!/usr/bin/env python3

# Function to generate TMSH commands for a single virtual server and append to files
def append_tmsh_commands_to_file(vs_name, pool_name, new_members, old_members, data_group, data_group_entries, original_data_group_entries, config_filename, rollback_filename):
    config_tmsh_commands = []
    rollback_tmsh_commands = []

    # Add new pool members and disable current pool members
    for new_member in new_members:
        ip_address = new_member.split(':')[0].split('/')[-1]  # Extract only the IP address
        config_tmsh_commands.append(f"# Add new member to {pool_name.split('/')[-1]} for {vs_name}")
        config_tmsh_commands.append(f"tmsh modify ltm pool {pool_name} members add {{ {new_member} {{ address {ip_address} }} }}")
        rollback_tmsh_commands.append(f"# Disable new member in {pool_name.split('/')[-1]} for {vs_name}")
        rollback_tmsh_commands.append(f"tmsh modify ltm pool {pool_name} members modify {{ {new_member} {{ session user-disabled }} }}")

    for old_member in old_members:
        config_tmsh_commands.append(f"# Disable current member in {pool_name.split('/')[-1]} for {vs_name}")
        config_tmsh_commands.append(f"tmsh modify ltm pool {pool_name} members modify {{ {old_member} {{ session user-disabled }} }}")
        rollback_tmsh_commands.append(f"# Enable old member in {pool_name.split('/')[-1]} for {vs_name}")
        rollback_tmsh_commands.append(f"tmsh modify ltm pool {pool_name} members modify {{ {old_member} {{ session user-enabled }} }}")
    
    # Add comment for replacing data group entries
    if data_group:
        config_tmsh_commands.append(f"# Replace all entries in Data Group for {vs_name}")
        data_group_entries_str = " ".join([f'"{entry}" {{ }}' for entry in data_group_entries])
        config_tmsh_commands.append(f"tmsh modify ltm data-group internal {data_group} records replace-all-with {{ {data_group_entries_str} }}")
        rollback_tmsh_commands.append(f"# Restore original entries in Data Group for {vs_name}")
        original_data_group_entries_str = " ".join([f'"{entry}" {{ }}' for entry in original_data_group_entries])
        rollback_tmsh_commands.append(f"tmsh modify ltm data-group internal {data_group} records replace-all-with {{ {original_data_group_entries_str} }}")

    # Append configuration commands to the config file
    with open(config_filename, 'a') as config_file:
        config_file.write(f"\n# Configuration for Virtual Server: {vs_name}\n")
        for cmd in config_tmsh_commands:
            config_file.write(cmd + '\n')
    
    # Append rollback commands to the rollback file
    with open(rollback_filename, 'a') as rollback_file:
        rollback_file.write(f"\n# Rollback for Virtual Server: {vs_name}\n")
        for cmd in rollback_tmsh_commands:
            rollback_file.write(cmd + '\n')


if __name__ == "__main__":
    print("Welcome to the TMSH script generator for multiple virtual servers.")

    # Get the filenames for configuration and rollback commands
    config_filename = input("Enter the output filename for configuration commands (e.g., 'tmsh_config_commands.txt'): ").strip()
    rollback_filename = input("Enter the output filename for rollback commands (e.g., 'tmsh_rollback_commands.txt'): ").strip()

    # Initialize/clear the files at the start
    with open(config_filename, 'w') as f:
        f.write("# TMSH Configuration Commands\n")
    with open(rollback_filename, 'w') as f:
        f.write("# TMSH Rollback Commands\n")

    while True:
        print("\nPlease enter the details for a new virtual server:")

        # Using `input()` to receive required inputs interactively
        vs_name = input("Enter virtual server name (e.g., '/Common/test-vs'): ").strip()
        pool_name = input("Enter pool name (e.g., '/Common/testpool'): ").strip()

        old_members = input("Enter old pool members (comma-separated, e.g., '/Common/10.10.10.10:80,/Common/10.10.10.11:80'): ").strip().split(',')
        new_members = input("Enter new pool members (comma-separated, e.g., '/Common/20.20.20.20:8443,/Common/20.20.20.21:8443'): ").strip().split(',')

        data_group = input("Enter data group name (leave blank if not applicable): ").strip()
        if data_group:
            data_group_entries = input("Enter data group entries (comma-separated, e.g., 'entry1,entry2,entry3'): ").strip().split(',')
            original_data_group_entries = input("Enter original data group entries for rollback (comma-separated): ").strip().split(',')
        else:
            data_group_entries = []
            original_data_group_entries = []

        # Append the TMSH commands for this virtual server
        append_tmsh_commands_to_file(
            vs_name=vs_name,
            pool_name=pool_name,
            new_members=new_members,
            old_members=old_members,
            data_group=data_group,
            data_group_entries=data_group_entries,
            original_data_group_entries=original_data_group_entries,
            config_filename=config_filename,
            rollback_filename=rollback_filename
        )

        print(f"Configuration commands for {vs_name} have been added to {config_filename}")
        print(f"Rollback commands for {vs_name} have been added to {rollback_filename}")

        # Ask if the user wants to enter another virtual server
        add_another = input("Do you want to add another virtual server? (yes/no): ").strip().lower()
        if add_another in ['no', 'n']:
            break

    print("\nTMSH script generation completed.")
    print(f"Final configuration commands can be found in {config_filename}")
    print(f"Final rollback commands can be found in {rollback_filename}")
