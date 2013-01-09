#!/usr/bin/python

import os
import sys
import argparse
import subprocess
import yaml

from drive import GoogleDrive, DRIVE_RW_SCOPE

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--config', '-f', default='gd.conf')
    p.add_argument('--text', '-T', action='store_const', const='text/plain',
            dest='filetype')
    p.add_argument('--html', '-H', action='store_const', const='text/html',
            dest='filetype')
    p.add_argument('docid')

    p.set_defaults(filetype='text/html')

    return p.parse_args()

def main():
    opts = parse_args()
    cfg = yaml.load(open(opts.config))
    gd = GoogleDrive(
            client_id=cfg['googledrive']['client id'],
            client_secret=cfg['googledrive']['client secret'],
            scopes=[DRIVE_RW_SCOPE],
            )

    gd.authenticate()

    md = gd.get_file_metadata(opts.docid)

    subprocess.call(['git','init',md['title']])
    os.chdir(md['title'])

    for rev in gd.revisions(opts.docid):
        with open('content', 'w') as fd:
            r = gd.session.get(rev['exportLinks'][opts.filetype])
            for chunk in r.iter_content():
                fd.write(chunk)
        subprocess.call(['git', 'add', 'content'])
        subprocess.call(['git', 'commit', '-m',
            'revision from %s' % rev['modifiedDate']])

if __name__ == '__main__':
    main()

