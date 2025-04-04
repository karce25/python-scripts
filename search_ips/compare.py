def compare_files(file1, file2):
    try:
        # Open the first file and read its lines into a set
        with open(file1, 'r') as f1:
            lines_file1 = set(f1.readlines())

        # Open the second file and read its lines into a set
        with open(file2, 'r') as f2:
            lines_file2 = set(f2.readlines())

        # Find common lines
        common_lines = lines_file1.intersection(lines_file2)

        # Output the common lines
        print("Lines in common:")
        for line in common_lines:
            print(line.strip())

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


# Replace 'file1.txt' and 'file2.txt' with the paths to your files
file1 = 'file1.txt'
file2 = 'file2.txt'

compare_files(file1, file2)
