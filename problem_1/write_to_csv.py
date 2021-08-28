import os
import csv
import datetime


def write(fields, rows):
    cwd = os.getcwd()
    date =  datetime.datetime.utcnow().strftime("%Y-%m-%dT%H-%m")
    file = '{}/{}.csv'.format(cwd, date)

    with open(file, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(fields)

        csvwriter.writerows(rows)
