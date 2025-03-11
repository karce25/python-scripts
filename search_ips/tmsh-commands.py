#!/usr/bin/env python3

# Inputs
vs_name = "/Common/test-vs"
snat_pool = "test-pool"
pool_name = "/Common/testpool"
old_members = ["/Common/10.10.10.10:80", "/Common/10.10.10.10:80"]
new_members = ["/Common/20.20.20.20:8443", "/Common/20.20.20.20:8443"]
data_group = " "
data_group_entries = [" "]
original_data_group_entries = [" "]
filename = "tmsh_commands.txt"

# Function to generate tmsh commands and save to a text file
def save_tmsh_commands_to_file(vs_name, snat_pool, pool_name, new_members, old_members, data_group, data_group_entries, original_data_group_entries, filename):
    tmsh_commands = []
    
    # Add new pool members and disable current pool members
    for new_member in new_members:
        ip_address = new_member.split(':')[0].split('/')[-1]  # Extract only the IP address
        tmsh_commands.append(f"# Add new member to {pool_name.split('/')[-1]}")
        tmsh_commands.append(f"tmsh modify ltm pool {pool_name} members add {{ {new_member} {{ address {ip_address} }} }}")
    
    for old_member in old_members:
        tmsh_commands.append(f"# Disable current member in {pool_name.split('/')[-1]}")
        tmsh_commands.append(f"tmsh modify ltm pool {pool_name} members modify {{ {old_member} {{ session user-disabled }} }}")

    # Add comment for replacing data group entries
    tmsh_commands.append(f"# Replace all entries in Data Group")
    # Replace Data Group entries
    data_group_entries_str = " ".join([f'"{entry}" {{ }}' for entry in data_group_entries])
    tmsh_commands.append(f"tmsh modify ltm data-group internal {data_group} records replace-all-with {{ {data_group_entries_str} }}")

    # Add rollback commands section
    tmsh_commands.append("\n# Rollback Commands\n")


    for new_member in new_members:
        # Rollback: Disable new pool members
        tmsh_commands.append(f"# Disable new member in {pool_name.split('/')[-1]}")
        tmsh_commands.append(f"tmsh modify ltm pool {pool_name} members modify {{ {new_member} {{ session user-disabled }} }}")
    
    for old_member in old_members:
        # Rollback: Enable old pool members
        tmsh_commands.append(f"# Enable old member in {pool_name.split('/')[-1]}")
        tmsh_commands.append(f"tmsh modify ltm pool {pool_name} members modify {{ {old_member} {{ session user-enabled }} }}")

    # Rollback: Restore original data group entries
    original_data_group_entries_str = " ".join([f'"{entry}" {{ }}' for entry in original_data_group_entries])
    tmsh_commands.append(f"# Restore original entries in Data Group")
    tmsh_commands.append(f"tmsh modify ltm data-group internal {data_group} records replace-all-with {{ {original_data_group_entries_str} }}")

    # Write commands to file
    with open(filename, 'w') as file:
        for cmd in tmsh_commands:
            file.write(cmd + '\n')



# Save tmsh commands to file
save_tmsh_commands_to_file(vs_name, snat_pool, pool_name, new_members, old_members, data_group, data_group_entries, original_data_group_entries, filename)
print(f"TMSH commands and rollback commands have been saved to {filename}")
