import csv

def read_csv(file_path):
    """Read the contents of a CSV file and return as a list of rows."""
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    return rows

def find_common_lines(file1, file2):
    """Find lines common to both CSV files."""
    rows_file1 = read_csv(file1)
    rows_file2 = read_csv(file2)

    # Convert rows to sets for efficient comparison
    set_file1 = set(tuple(row) for row in rows_file1)
    set_file2 = set(tuple(row) for row in rows_file2)

    # Find common lines
    common_lines = set_file1.intersection(set_file2)

    return common_lines

def main():
    # Replace these file names with the paths to your own files
    file1 = 'file1.csv'
    file2 = 'file2.csv'

    common_lines = find_common_lines(file1, file2)

    # Output the common lines
    if common_lines:
        print("Common lines between the two files:")
        for line in common_lines:
            print(line)
    else:
        print("No common lines found.")

if __name__ == '__main__':
    main()
