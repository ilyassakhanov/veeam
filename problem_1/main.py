#!/usr/bin/python3

from datetime import datetime,timedelta
from subprocess import run
import sys, getopt
import time
import get_data
import write_to_csv

def run(path, start_time, end_time):
    continue_loop = True
    pid = get_data.start_process(path)
    fields = ['time', 'cpu-usage', 'resident-set-size', 'virtual-memory-size']
    rows = []
    while continue_loop:
        if start_time < end_time:
            continue_loop = True
        else:
            continue_loop = False
        data = get_data.main(pid)
        data.insert(0, start_time.strftime("%Y-%m-%dT%H-%m"))
        rows.append(data)
        time.sleep(60)
        start_time += timedelta(minutes=1)

    write_to_csv.write(fields, rows=rows)

    

def main(argv):
    path = ''
    start_time = ''
    end_time = ''
    start_time_str = ''
    end_time_str = ''
    try:
        opts,args = getopt.getopt(argv, ":h", ["path=", "start_time=", "end_time="])
    except getopt.GetoptError:
        print('python3 main.py --path <path> --start_time YYYY-MM-DDThh-mm --end_time YYYY-MM-DDThh-mm')
        sys.exit(1)
    
    for opt, arg in opts:                
        if opt == "-h":
            print('python3 main.py --path <path> --start_time YYYY-MM-DDThh-mm --end_time YYYY-MM-DDThh-mm')
        elif opt == "--path":
            path = arg
        elif opt == "--start_time":
            start_time_str = arg
        elif opt == "--end_time":
            end_time_str = arg

    if start_time_str == '' or end_time_str == '':
        print('No time was provided')
        sys.exit(1)
    try:
        start_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H-%M")
        end_time = datetime.strptime(end_time_str, "%Y-%m-%dT%H-%M")
    except TypeError:
        print('Time failed to parse')
        sys.exit(1)
    if start_time == '' or end_time == '':
        print("Error with processing time")
        sys.exit(1)
    run(path, start_time, end_time)
    return
      


if __name__ == "__main__":
    main(sys.argv[1:])