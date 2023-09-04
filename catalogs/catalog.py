import csv
import re


def get_catalog(file=None):
    # Initialize an empty dictionary to store the data
    dict = {}

    # Select collumns to read
    if file == 'Messier.csv':
        ii = 4
        jj = 5
    elif file == 'Starname.csv':
        ii = 7
        jj = 8

    # Open and read the CSV file
    with open(file, mode='r', newline='') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)  # Skip the header row

        for row in csv_reader:
            # Object
            key = row[0]

            # AR
            ar = row[ii]
            match = re.match(r'(\d+)h (\d+(?:\.\d+)?)m', ar)
            try:
                ar_hours = int(match.group(1))
                ar_minutes = int(float(match.group(2)))
                try:
                    ar_seconds = int(float("0." + match.group(2).split('.')[1]) * 60)
                except:
                    ar_seconds = 0
            except:
                pass

            # DE
            de = row[jj]
            if file == 'Messier.csv':
                match = re.match(r"(-?\d+)d (\d+)'", de)
                try:
                    de_degrees = int(match.group(1))
                    de_minutes = int(match.group(2))
                    de_seconds = 0
                except:
                    pass
            elif file == 'Starname.csv':
                match = re.match(r"(-?\d+)d (\d+\.\d+)'", de)
                try:
                    de_degrees = int(match.group(1))
                    de_minutes = int(float(match.group(2)))
                    de_seconds = int(float("0." + match.group(2).split('.')[1]) * 60)
                except:
                    pass
            # Check if the key already exists in the dictionary
            if key not in dict:
                dict[key] = [ar_hours, ar_minutes, ar_seconds, de_degrees, de_minutes, de_seconds]
    return dict


def join_catalogs():
    catalogs = {
        'Messier': get_catalog('Messier.csv'),
        'Stars': get_catalog('Starname.csv')
    }

    # Merge the dictionaries using the update() method
    catalog_full = catalogs['Messier'].copy()
    catalog_full.update(catalogs['Stars'])

    # Sort the merged dictionary by keys in alphabetical order
    # return dict(sorted(catalog_full.items()))

    # Return the catalog
    return catalog_full


catalog = join_catalogs()
