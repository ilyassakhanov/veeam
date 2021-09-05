import sys
from datetime import datetime
from typing import final


def log_main(pyrobocopy, raw_log):
    try:
        logfile = open(pyrobocopy.logfile_path, "a")
    except SyntaxError:
        print("Wrong logfile path!")
        sys.exit(1)
    raw_log_str = get_raw_log_str(raw_log)
    composed_log = compose_log(raw_log_str)
    print(raw_log_str)
    logfile.write(composed_log)
    logfile.close()

def get_raw_log_str(raw_log):
    final_log = ''
    for log in raw_log:
        final_log += (str(log) + ' ')
    return final_log

def compose_log(raw_log):
    composed_log ="[{}] {}".format(datetime.utcnow().strftime("%Y-%m-%dT%H-%M"), raw_log)
    return composed_log