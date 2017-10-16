import os.path
import sys
import shutil
import subprocess
print("Updating ucsc tables...")
exec(open('ucsc_downloader.py').read())
exec(open('updater.py').read())
if (os.path.exists('db/readme_new')):
    shutil.move('db/readme_new','db/readme_old')
print('recreating the database...')
exec(open('db_creator.py').read())
print('assinging domains to exons, this will take a while.')
exec(open('domains_to_exons.py').read())
