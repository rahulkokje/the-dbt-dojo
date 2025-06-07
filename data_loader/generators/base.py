import csv

class BaseGenerator:
    def save_to_csv(self, filepath, headers, rows):
        with open(filepath, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(rows)
