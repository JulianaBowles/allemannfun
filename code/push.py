#!/usr/bin/env python

import argparse
import keyring
import getpass
import os.path
import sys
import subprocess

SERVICE="www.allemannfun.org.uk"
USER="web@allemannfun.org.uk"
HOST="ftp.allemannfun.org.uk"

if __name__ == "__main__":
    site = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]),'..','site'))
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-s","--site-dir",default=site,help="the directory containing the site to be uploaded")
    parser.add_argument("-p","--set-password",default=False,action="store_true",help="store the password")
    args = parser.parse_args()

    # sort out password
    if args.set_password:
        pw = getpass.getpass()
        keyring.set_password(SERVICE,USER,pw)
        sys.exit(0)
    else:
        pw = keyring.get_password(SERVICE,USER)
        if pw==None:
            parser.error("No password for user:%s service:%s in keyring"%(USER,SERVICE))
    
    # make sure site directory exists
    if not os.path.isdir(args.site_dir):
        parser.error("site directory %s does not exist"%args.site_dir)

    print args.site_dir
        
    # construct lftp script
    lftpscript = """ 
set ftp:ssl-allow off
set ftp:list-options -a;
open -u {user},{password} -p 21 ftp://{host};
lcd {site};
mirror --reverse \
       --delete \
       --verbose \
       --exclude-glob *~
""".format(user=USER,password=pw,host=HOST,site=args.site_dir)

    try:
        subprocess.check_call(["lftp","-c",lftpscript])
    except subprocess.CalledProcessError,val:
        print val
        sys.exit(1)
