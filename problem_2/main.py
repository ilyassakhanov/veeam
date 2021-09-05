#!/usr/bin/python3


import shutil
import sys, getopt

def run():

    return


def main(argv):
    path = ''
    sync_interval_str = ''
    logfile_path = ''

    try:
        opts, args = getopt.getopt(argv, ":h", ["original-folder-path=", "replica-folder-path=", "interval=", "logfile="])
    except getopt.GetoptError:
        print('python3 main.py  --original-folder-path <path> --replica-folder-path <path> --interval <sync interval> --logfile <logfile path>')
        sys.exit(1)
    
    for opt, arg in opts:                
        if opt == "-h":
            print('python3 main.py  --original-folder-path <path> --replica-folder-path <path> --interval <number in minutes> --logfile <logfile path>')
        elif opt == "--original-folder-path":
            path = arg
        elif opt == "-interval":
            sync_interval_str = arg
        elif opt == "--logfile":
            logfile_path = arg
        

    if path == "" or sync_interval_str == '' or logfile_path == '':
        print("Wrong arguments were provided")
        sys.exit(1)

    sync_interval = int(sync_interval_str)
    
   
    return



if __name__ == "__main__":
    main(sys.argv[1:])