def find_lines(file1, file2):
    try:
        # Open and read files
        with open(file1, 'r') as f1, open(file2, 'r') as f2:
            lines_file1 = set(f1.readlines())  # Read lines from file1
            lines_file2 = set(f2.readlines())  # Read lines from file2

        # Calculate matching and missing lines
        matching_lines = lines_file1.intersection(lines_file2)  # Lines present in both files
        missing_lines = lines_file1.difference(lines_file2)     # Lines in file1 but not in file2

        # Write matching lines to `matching_lines.txt`
        with open('matching_lines.txt', 'w') as matching_file:
            matching_file.writelines(line for line in matching_lines)

        # Write missing lines to `missing_lines.txt`
        with open('missing_lines.txt', 'w') as missing_file:
            missing_file.writelines(line for line in missing_lines)

        # Print summary
        print(f"Matching lines ({len(matching_lines)}):")
        for line in matching_lines:
            print(line.strip())  # Strip removes leading/trailing whitespace
      
        print(f"\nMissing lines ({len(missing_lines)}):")
        for line in missing_lines:
            print(line.strip())

        print("\nResults saved to 'matching_lines.txt' and 'missing_lines.txt'.")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


# Dynamic input for file paths
file1 = input("Enter the path to file1: ").strip()
file2 = input("Enter the path to file2: ").strip()
find_lines(file1, file2)
