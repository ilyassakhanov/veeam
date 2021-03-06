#!/usr/bin/python3

""" pyrobocopy.py -

    Version: 1.0
    
    Report the difference in content
    of two directories, synchronize or
    update a directory from another, taking
    into account time-stamps of files etc.

    By Anand B Pillai 

    (This program is inspired by the windows
    'Robocopy' program.)

    Mod  Nov 11 Rewrote to use the filecmp module.

    5/9/2021 Update:
        This file has become a Frankestein to satisfy a need of this problem
"""

import os, stat
import time
import shutil
import filecmp
import log
from datetime import datetime
from threading import Timer


def usage():
    return """
Pyrobocopy: Command line directory diff, synchronization, update & copy

Author: Anand Pillai

Usage: %s <sourcedir> <targetdir> Options

Main Options:\n
\t-d --diff         - Only report difference between sourcedir and targetdir
\t-s, --synchronize - Synchronize content between sourcedir and targetdir
\t-u, --update      - Update existing content between sourcedir and targetdir

Additional Options:\n
\t-p, --purge       - Purge files when synchronizing (does not purge by default).
\t-f, --force       - Force copying of files, by trying to change file permissions.
\t-n, --nodirection - Update files in source directory from target
\t                    directory (only updates target from source by default).
\t-c, --create      - Create target directory if it does not exist (By default,
\t                    target directory should exist.)
\t-m, --modtime     - Only compare file's modification times for an update (By default,
\t                    compares source file's creation time also).
"""                   



class PyRobocopier:
    """ An advanced directory synchronization, updation
    and file copying class """

    prog_name = "pyrobocopy.py"
    
    def __init__(self):

        self.__dir1 = ''
        self.__dir2 = ''
        self.__dcmp = None
        
        self.__copyfiles = True
        self.__forcecopy = False
        self.__copydirection = 0
        self.__updatefiles = True
        self.__creatdirs = True
        self.__purge =False
        self.__maketarget =False
        self.__modtimeonly =False
        self.__mainfunc = None
        
        # stat vars
        self.__numdirs =0
        self.__numfiles =0
        self.__numdelfiles =0
        self.__numdeldirs =0     
        self.__numnewdirs =0
        self.__numupdates =0
        self.__starttime = 0.0
        self.__endtime = 0.0
        
        # failure stat vars
        self.__numcopyfld =0
        self.__numupdsfld =0
        self.__numdirsfld =0
        self.__numdelffld  =0
        self.__numdeldfld  =0

    def parse_args(self, arguments):
        """ Parse arguments """
        
        import getopt

        shortargs = "supncm"
        longargs = ["synchronize=", "update=", "purge=", "nodirection=", "create=", "modtime="]

        try:
            optlist, args = getopt.getopt( arguments, shortargs, longargs )
        except getopt.GetoptError as e:
            log.log_main(self,e)
            return None

        allargs = []
        if len(optlist):
            allargs = [x[0] for x in optlist]
            
        allargs.extend( args )
        self.__setargs( allargs )
    
    def parse_args_2(self, arguments):
        self.__interval = 0
        sync_interval_str = ''

        import getopt

        try:
            opts, args = getopt.getopt(arguments, ":h", ["original-folder-path=", "replica-folder-path=", "interval=", "logfile="])
        except getopt.GetoptError:
            log.log_main(self, 'python3 main.py  --original-folder-path <path> --replica-folder-path <path> --interval <sync interval> --logfile <logfile path>')
            sys.exit(1)
    
        for opt, arg in opts:   
              
            if opt == "-h":
                log.log_main(self, ('python3 main.py  --original-folder-path <path> --replica-folder-path <path> --interval <number in minutes> --logfile <logfile path>'))
            elif opt == "--original-folder-path":
                original_path = arg
            elif opt == "--replica-folder-path":
                replica_path = arg
            elif opt == "--interval":
                sync_interval_str = arg
            elif opt == "--logfile":
                self.logfile_path = arg

        try:
            self.__interval = int(sync_interval_str)
        except ValueError:
            log.log_main(self,("Invalid interval!"))
            sys.exit(1) 
       
        if (original_path == '' or replica_path == '') or (self.__interval == 0 or self.logfile_path == ''):
            log.log_main(self,"Wrong arguments were provided")
            sys.exit(1)

        self.__dir1 = original_path
        self.__dir2 = replica_path
        self.__mainfunc = self.synchronize

    def __setargs(self, argslist):
        """ Sets internal variables using arguments """
        
        for option in argslist:
            if option.lower() in ('-s', '--synchronize'):
                self.__mainfunc = self.synchronize
            elif option.lower() in ('-u', '--update'):
                self.__mainfunc = self.update
            elif option.lower() in ('-d', '--diff'):
                self.__mainfunc = self.dirdiff
            elif option.lower() in ('-p', '--purge'):
                self.__purge = True
            elif option.lower() in ('-n', '--nodirection'):
                self.__copydirection = 2
            elif option.lower() in ('-f', '--force'):
                self.__forcecopy = True
            elif option.lower() in ('-c', '--create'):
                self.__maketarget = True
            elif option.lower() in ('-m', '--modtime'):
                self.__modtimeonly = True                            
            else:
                if self.__dir1=='':
                    self.__dir1 = option
                elif self.__dir2=='':
                    self.__dir2 = option
                
        if self.__dir1=='' or self.__dir2=='':
            sys.exit("Argument Error: Directory arguments not given!")
        if not os.path.isdir(self.__dir1):
            sys.exit("Argument Error: Source directory does not exist!")
        if not self.__maketarget and not os.path.isdir(self.__dir2):
            sys.exit("Argument Error: Target directory %s does not exist! (Try the -c option)." % self.__dir2)
        if self.__mainfunc is None:
            sys.exit("Argument Error: Specify an action (Diff, Synchronize or Update) ")

        self.__dcmp = filecmp.dircmp(self.__dir1, self.__dir2)

    def do_work(self):
        """ Do work """

        self.__starttime = time.time()
        
        if not os.path.isdir(self.__dir2):
            if self.__maketarget:
                log.log_main(self,'Creating directory', self.__dir2)
                try:
                    os.makedirs(self.__dir2)
                except Exception as e:
                    log.log_main(self,e)
                    return None

        # All right!
        self.__mainfunc()
        self.__endtime = time.time()
        
    def __dowork(self, dir1, dir2, copyfunc = None, updatefunc = None):
        """ Private attribute for doing work """
        
        log.log_main(self,('Source directory: ', dir1, ':'))

        self.__numdirs += 1
        self.__dcmp = filecmp.dircmp(dir1, dir2)
        
        # Files & directories only in target directory
        if self.__purge:
            for f2 in self.__dcmp.right_only:
                fullf2 = os.path.join(dir2, f2)
                log.log_main(self,'Deleting ',fullf2)
                try:
                    if os.path.isfile(fullf2):
                        
                        try:
                            os.remove(fullf2)
                            self.__numdelfiles += 1
                        except OSError as e:
                            log.log_main(self,e)
                            self.__numdelffld += 1
                    elif os.path.isdir(fullf2):
                        try:
                            shutil.rmtree( fullf2, True )
                            self.__numdeldirs += 1
                        except shutil.Error as e:
                            log.log_main(self,e)
                            self.__numdeldfld += 1
                                
                except Exception as e: # of any use ?
                    log.log_main(self,e)
                    continue


        # Files & directories only in source directory
        for f1 in self.__dcmp.left_only:
            try:
               st = os.stat(os.path.join(dir1, f1))
            except os.error:
                continue

            if stat.S_ISREG(st.st_mode):
                if copyfunc: copyfunc(f1, dir1, dir2)
            elif stat.S_ISDIR(st.st_mode):
                fulld1 = os.path.join(dir1, f1)
                fulld2 = os.path.join(dir2, f1)
                
                if self.__creatdirs:
                    try:
                        # Copy tree
                        log.log_main(self,'Copying tree', fulld2)
                        shutil.copytree(fulld1, fulld2)
                        self.__numnewdirs += 1
                        log.log_main(self,'Done.')
                    except shutil.Error as e:
                        log.log_main(self,e)
                        self.__numdirsfld += 1
                        
                        # jump to next file/dir in loop since this op failed
                        continue

                # Call tail recursive
                # if os.path.exists(fulld2):
                #    self.__dowork(fulld1, fulld2, copyfunc, updatefunc)

        # common files/directories
        for f1 in self.__dcmp.common:
            try:
                st = os.stat(os.path.join(dir1, f1))
            except os.error:
                continue

            if stat.S_ISREG(st.st_mode):
                if updatefunc: updatefunc(f1, dir1, dir2)
            elif stat.S_ISDIR(st.st_mode):
                fulld1 = os.path.join(dir1, f1)
                fulld2 = os.path.join(dir2, f1)
                # Call tail recursive
                self.__dowork(fulld1, fulld2, copyfunc, updatefunc)
                

    def __copy(self, filename, dir1, dir2):
        """ Private function for copying a file """

        # NOTE: dir1 is source & dir2 is target
        if self.__copyfiles:

            log.log_main(self,'Copying file', filename, dir1, dir2)
            try:
                if self.__copydirection== 0 or self.__copydirection == 2:  # source to target
                    
                    if not os.path.exists(dir2):
                        if self.__forcecopy:
                            os.chmod(os.path.dirname(dir2), 0o777)
                        try:
                            os.makedirs(dir1)
                        except OSError as e:
                            log.log_main(self,e)
                            self.__numdirsfld += 1
                        
                    if self.__forcecopy:
                        os.chmod(dir2, 0o777)

                    sourcefile = os.path.join(dir1, filename)
                    try:
                        shutil.copy(sourcefile, dir2)
                        self.__numfiles += 1
                    except (IOError, OSError) as e:
                        log.log_main(self,e)
                        self.__numcopyfld += 1
                    
                elif self.__copydirection==1 or self.__copydirection == 2: # target to source 

                    if not os.path.exists(dir1):
                        if self.__forcecopy:
                            os.chmod(os.path.dirname(dir1), 0o777)

                        try:
                            os.makedirs(dir1)
                        except OSError as e:
                            log.log_main(self,e)
                            self.__numdirsfld += 1                          

                    targetfile = os.path.abspath(os.path.join(dir1, filename))
                    if self.__forcecopy:
                        os.chmod(dir1, 0o777)

                    sourcefile = os.path.join(dir2, filename)
                    
                    try:
                        shutil.copy(sourcefile, dir1)
                        self.__numfiles += 1
                    except (IOError, OSError) as e:
                        log.log_main(self,e)
                        self.__numcopyfld += 1
                    
            except Exception as e:
                log.log_main(self,'Error copying  file', filename, e)

    def __cmptimestamps(self, filest1, filest2):
        """ Compare time stamps of two files and return True
        if file1 (source) is more recent than file2 (target) """

        return ((filest1.st_mtime > filest2.st_mtime) or \
                   (not self.__modtimeonly and (filest1.st_ctime > filest2.st_mtime)))
    
    def __update(self, filename, dir1, dir2):
        """ Private function for updating a file based on
        last time stamp of modification """

        log.log_main(self,'Updating file', filename)
        
        # NOTE: dir1 is source & dir2 is target        
        if self.__updatefiles:

            file1 = os.path.join(dir1, filename)
            file2 = os.path.join(dir2, filename)

            try:
                st1 = os.stat(file1)
                st2 = os.stat(file2)
            except os.error:
                return -1

            # Update will update in both directions depending
            # on the timestamp of the file & copy-direction.

            if self.__copydirection==0 or self.__copydirection == 2:

                # Update file if file's modification time is older than
                # source file's modification time, or creation time. Sometimes
                # it so happens that a file's creation time is newer than it's
                # modification time! (Seen this on windows)
                if self.__cmptimestamps( st1, st2 ):
                    log.log_main(self,'Updating file ', file2) # source to target
                    try:
                        if self.__forcecopy:
                            os.chmod(file2, 0o666)

                        try:
                            shutil.copy(file1, file2)
                            self.__numupdates += 1
                            return 0
                        except (IOError, OSError) as e:
                            log.log_main(self,e)
                            self.__numupdsfld += 1
                            return -1

                    except Exception as e:
                        log.log_main(self,e)
                        return -1

            elif self.__copydirection==1 or self.__copydirection == 2:

                # Update file if file's modification time is older than
                # source file's modification time, or creation time. Sometimes
                # it so happens that a file's creation time is newer than it's
                # modification time! (Seen this on windows)
                if self.__cmptimestamps( st2, st1 ):
                    log.log_main(self,'Updating file ', file1) # target to source
                    try:
                        if self.__forcecopy:
                            os.chmod(file1, 0o666)

                        try:
                            shutil.copy(file2, file1)
                            self.__numupdates += 1
                            return 0
                        except (IOError, OSError) as e:
                            log.log_main(self,e)
                            self.__numupdsfld += 1
                            return -1
                        
                    except Exception as e:
                        log.log_main(self,e)
                        return -1

        return -1

    def __dirdiffandcopy(self, dir1, dir2):
        """ Private function which does directory diff & copy """
        self.__dowork(dir1, dir2, self.__copy)

    def __dirdiffandupdate(self, dir1, dir2):
        """ Private function which does directory diff & update  """        
        self.__dowork(dir1, dir2, None, self.__update)

    def __dirdiffcopyandupdate(self, dir1, dir2):
        """ Private function which does directory diff, copy and update (synchro) """               
        self.__dowork(dir1, dir2, self.__copy, self.__update)

    def __dirdiff(self):
        """ Private function which only does directory diff """

        if self.__dcmp.left_only:
            log.log_main(self,'Only in', self.__dir1)
            for x in self.__dcmp.left_only:
                log.log_main(self,'>>', x)

        if self.__dcmp.right_only:
            log.log_main(self,'Only in', self.__dir2)
            for x in self.__dcmp.right_only:
                log.log_main(self,'<<', x)

        if self.__dcmp.common:
            log.log_main(self,'Common to', self.__dir1,' and ',self.__dir2)
            log.log_main(self,)
            for x in self.__dcmp.common:
                log.log_main(self,'--', x)
        else:
            log.log_main(self,'No common files or sub-directories!')

    def synchronize(self):
        """ Synchronize will try to synchronize two directories w.r.t
        each other's contents, copying files if necessary from source
        to target, and creating directories if necessary. If the optional
        argument purge is True, directories in target (dir2) that are
        not present in the source (dir1) will be deleted . Synchronization
        is done in the direction of source to target """

        self.__copyfiles = True
        self.__updatefiles = True
        self.__creatdirs = True
        self.__copydirection = 0

        log.log_main(self,('Synchronizing directory', self.__dir2, 'with', self.__dir1 ,'\n'))
        self.__dirdiffcopyandupdate(self.__dir1, self.__dir2)

    def update(self):
        """ Update will try to update the target directory
        w.r.t source directory. Only files that are common
        to both directories will be updated, no new files
        or directories are created """

        self.__copyfiles = False
        self.__updatefiles = True
        self.__purge = False
        self.__creatdirs = False

        log.log_main(self,'Updating directory', self.__dir2, 'from', self.__dir1 , '\n')
        self.__dirdiffandupdate(self.__dir1, self.__dir2)

    def dirdiff(self):
        """ Only report difference in content between two
        directories """

        self.__copyfiles = False
        self.__updatefiles = False
        self.__purge = False
        self.__creatdirs = False
        self.__updatefiles = False
        
        log.log_main(self,'Difference of directory ', self.__dir2, 'from', self.__dir1 , '\n')
        self.__dirdiff()
        
    def report(self):
        """ Print report of work at the end """

        # We need only the first 4 significant digits
        tt = (str(self.__endtime - self.__starttime))[:4]
        
        log.log_main(self,('Python robocopier finished in',tt, 'seconds. \n'))
        log.log_main(self,(self.__numdirs, 'directories parsed,',self.__numfiles, 'files copied.'))
        if self.__numdelfiles:
            log.log_main(self,(self.__numdelfiles, 'files were purged.'))
        if self.__numdeldirs:
            log.log_main(self,(self.__numdeldirs, 'directories were purged.'))
        if self.__numnewdirs:
            log.log_main(self,(self.__numnewdirs, 'directories were created.'))
        if self.__numupdates:
            log.log_main(self,(self.__numupdates, 'files were updated by timestamp.'))

        # Failure stats
        log.log_main(self,'\n')
        if self.__numcopyfld:
            log.log_main(self,(self.__numcopyfld, 'files could not be copied.'))
        if self.__numdirsfld:
            log.log_main(self,(self.__numdirsfld, 'directories could not be created.'))
        if self.__numupdsfld:
            log.log_main(self,(self.__numupdsfld, 'files could not be updated.'))
        if self.__numdeldfld:
            log.log_main(self,(self.__numdeldfld, 'directories could not be purged.'))
        if self.__numdelffld:
            log.log_main(self,(self.__numdelffld, 'files could not be purged.'))
    
    def sync_scheduler(self):
        x = datetime.utcnow()
        y = x.replace(minute=x.minute + self.__interval)
        delta_t = (y-x).seconds
        copier.do_work()
        Timer(delta_t, self.sync_scheduler).start()
        
if __name__=="__main__":
    import sys

    copier = PyRobocopier()
    copier.parse_args_2(sys.argv[1:])
    copier.sync_scheduler()

    # print report at the end
    copier.report()
