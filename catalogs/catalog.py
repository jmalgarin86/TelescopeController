import csv
import re

def csv_to_dict(csv_file):
    """
    Reads a CSV file and converts it to a dictionary.

    Args:
        csv_file (str): File name for the CSV file.

    Returns:
        dict: Dictionary containing the data from the CSV file.
    """
    data = {}
    with open(csv_file, 'r') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            for key, value in row.items():
                if key in data:
                    data[key].append(value)
                else:
                    data[key] = [value]
    return data


def write_dict_to_csv(data, csv_file):
    """
    Writes a dictionary to a CSV file.

    Args:
        data (dict): Dictionary containing the data to be written to the CSV file.
        csv_file (str): File name for the CSV file.
    """
    with open(csv_file, 'w', newline='') as csvfile:
        fieldnames = data.keys()
        csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        csv_writer.writeheader()

        for i in range(len(data[list(data.keys())[0]])):
            row_data = {key: data[key][i] for key in fieldnames}
            csv_writer.writerow(row_data)

    print(f'CSV file "{csv_file}" has been created successfully.')


def update_csv_column(csv_file, heading, new_values):
    """
    Updates an entire column in the CSV file corresponding to the specified heading.

    Args:
        csv_file (str): File name for the CSV file.
        heading (str): Heading of the column to be updated.
        new_values (list): List of new values for the specified column.
    """
    rows = []
    with open(csv_file, 'r') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        fieldnames = csv_reader.fieldnames

        for row in csv_reader:
            if heading in fieldnames:
                row[heading] = new_values.pop(0)
            rows.append(row)

    with open(csv_file, 'w', newline='') as csvfile:
        csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        csv_writer.writeheader()
        csv_writer.writerows(rows)

    print(f'Column "{heading}" in CSV file "{csv_file}" has been updated successfully.')


def add_or_update_field(csv_file, field_name, field_values):
    """
    Adds a new field to a CSV file. If the field already exists, it updates the values.

    Args:
        csv_file (str): File name for the CSV file.
        field_name (str): Name of the field to be added or updated.
        field_values (list): List of values for the specified field.
    """
    data = {}
    fieldnames = []

    # Read existing data from CSV file
    try:
        with open(csv_file, 'r') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            fieldnames = csv_reader.fieldnames

            # Populate data dictionary with existing data
            for field in fieldnames:
                data[field] = []
            for row in csv_reader:
                for field in fieldnames:
                    data[field].append(row[field])
    except FileNotFoundError:
        pass

    # Update or add new field values
    data[field_name] = field_values

    # Write data back to CSV file
    with open(csv_file, 'w', newline='') as csvfile:
        fieldnames = list(data.keys())
        csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        csv_writer.writeheader()

        for i in range(len(field_values)):
            row_data = {key: data[key][i] for key in fieldnames}
            csv_writer.writerow(row_data)

    print(f'Field "{field_name}" has been added or updated in CSV file "{csv_file}".')

# Example usage:
csv_file = 'catalog.csv'
catalog = csv_to_dict(csv_file)
