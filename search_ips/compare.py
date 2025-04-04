def find_missing_lines(file1, file2):
    try:
        # Open and read lines from file1
        with open(file1, 'r') as f1:
            lines_file1 = set(f1.readlines())
        
        # Open and read lines from file2
        with open(file2, 'r') as f2:
            lines_file2 = set(f2.readlines())
        
        # Find lines that are in file1 but not in file2
        missing_lines = lines_file1.difference(lines_file2)
        
        # Output the missing lines
        print("Lines in file1 but not in file2:")
        if missing_lines:
            for line in missing_lines:
                print(line.strip())  # Strip removes leading/trailing whitespace/newlines
        else:
            print("All lines in file1 are also present in file2.")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


# Replace 'file1.txt' and 'file2.txt' with the full paths to your files
file1 = r"C:\Users\karce\file1.txt"
file2 = r"C:\Users\karce\file2.txt"

find_missing_lines(file1, file2)
