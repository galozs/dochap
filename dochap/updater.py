# ADD NEW DATA FROM UCSC, AND FIND WAY TO AUTO DOWNLOAD AND CHECK FOR UPDATE FOR IT
# NEED TABLE OF ALIASES FROM TRANSCRIPT_ID TO GENE_NAME
# NEED TABLE OF TRANSCRIPT DATA LIKE EXONS LOCATIONS, AND CDS LOCATIONS WE NEED
from ftplib import FTP
import tarfile
import sys
import os.path
import subprocess
import progressbar
import pathlib
import conf
from sh import gunzip
prot_path = "genomes/{}/protein/protein.gbk.gz"
filename = "protein.gbk.gz"
# species is Homo_sapiens, Mus_musculus
extract_path = "db/{}/"
readme_file = 'genomes/{}/README_CURRENT_RELEASE'
print ("connecting to ftp.ncbi.nlm.nih.gov...")
ftp = FTP("ftp.ncbi.nlm.nih.gov")
print ("logging in...")
ftp.login()
prompt = 'Update {} data? (y/N): '
skipping_prompt = 'Skipping {}'
for specie in conf.species:
    user_input = input(prompt.format(specie))
    if user_input.lower() != 'y':
        print(skipping_prompt.format(specie))
        continue
    formatted_extract_path = extract_path.format(specie)
    print ("Creating directory {} ".format(formatted_extract_path))
    pathlib.Path(formatted_extract_path).mkdir(parents=True, exist_ok=True)
    print ("downloading {} data".format(specie))
    ftp.sendcmd("TYPE i")
    readme_size = ftp.size(readme_file.format(specie))
    readme_progress = progressbar.AnimatedProgressBar(end=readme_size,width=10)
    if os.path.isfile(formatted_extract_path+ "readme_old"):
        print("readme_old found, checking againts existing database...")
    else:
        print("readme_old not found, downloading new database...")
    print ("downloading readme_file...")
    with open(formatted_extract_path+"readme_new",'w') as f:
        def callback(chunk):
            f.write(chunk)
            readme_progress + len(chunk)
            readme_progress.show_progress()
        ftp.retrlines("RETR " + readme_file.format(specie),callback)
        readme_progress+readme_size
        readme_progress.show_progress()
    # empty line
    print()
    new_readme_lines=[]
    old_readme_lines=[]
    if os.path.isfile(formatted_extract_path+"readme_old"):
        with open(formatted_extract_path+"readme_old","r") as readme:
            old_readme_lines = readme.readlines()
    with open(formatted_extract_path+"readme_new","r") as new_readme:
        new_readme_lines = new_readme.readlines()
    if new_readme_lines == old_readme_lines and os.path.isfile(formatted_extract_path+"aliases.db") and os.path.isfile(formatted_extract_path+"comb.db"):
        print("{} database is up to date.".format(specie))
    elif not os.path.isfile(formatted_extract_path + 'protein.gbk'):
        print ("downloading " + filename + "...")
        ftp.sendcmd("TYPE i")
        archive_size = ftp.size(prot_path.format(specie))
        archive_progress = progressbar.AnimatedProgressBar(end=archive_size,width=10)
        with open(formatted_extract_path+filename,'wb') as f:
            def callback(chunk):
                f.write(chunk)
                archive_progress + len(chunk)
                archive_progress.show_progress()
            ftp.retrbinary("RETR " + prot_path.format(specie),callback)
            archive_progress + archive_size
            archive_progress.show_progress()
            print()
            print ("download complete.")
        gunzip(formatted_extract_path+filename,'-f')
    print ("Moving new readme file...")
    os.rename(formatted_extract_path+"readme_new", formatted_extract_path+"readme_old")
print ("starting database upgrade...")
ftp.quit()
#print ("EXITING NOW, PLEASE REMOVE ME")
#sys.exit(2)
# if the python script calls the updater.sh permission issues may arise
#subprocess.call(['./updater.sh'])
