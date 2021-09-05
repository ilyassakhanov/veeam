import sys
from datetime import datetime


def log_main(pyrobocopy, raw_log):
    try:
        logfile = open(pyrobocopy.logfile_path, "a")
    except SyntaxError:
        print("Wrong logfile path!")
        sys.exit(1)
    composed_log = compose_log(raw_log)
    logfile.write(composed_log)
    logfile.close()


def compose_log(raw_log):
    composed_log ="[{}] {} \n".format(datetime.utcnow().strftime("%Y-%m-%dT%H-%M"), raw_log)
    return composed_log