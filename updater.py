from ftplib import FTP
import tarfile
import os.path
import subprocess
import progressbar
prot_path = "genomes/Mus_musculus/protein/protein.gbk.gz"
filename = "protein.gbk.gz"
extract_path = "db/"
readme_file = 'genomes/Mus_musculus/README_CURRENT_RELEASE'

print ("connecting to ftp.ncbi.nlm.nih.gov...")
ftp = FTP("ftp.ncbi.nlm.nih.gov")
print ("logging in...")
ftp.login()
readme_size = ftp.size(readme_file)

readme_progress = progressbar.AnimatedProgressBar(end=readme_size,width=20)

print ("downloading readme_file...")
with open(extract_path+"readme_new",'w') as f:
    def callback(chunk):
        f.write(chunk)
        readme_progress + len(chunk)
        readme_progress.show_progress()
    ftp.retrlines("RETR " + readme_file,callback)
    readme_progress+readme_size
    readme_progress.show_progress()
# empty line
print()
new_readme_lines=[]
old_readme_lines=[]
if os.path.isfile(extract_path+"readme_old"):
    with open(extract_path+"readme_old","r") as readme:
        old_readme_lines = readme.readlines()
with open(extract_path+"readme_new","r") as new_readme:
    new_readme_lines = new_readme.readlines()
if new_readme_lines == old_readme_lines:
    print("database is up to date.")
    ftp.quit()
else:
    print ("downloading " + filename + "...")
    ftp.sendcmd("TYPE i")
    archive_size = ftp.size(prot_path)
    archive_progress = progressbar.AnimatedProgressBar(end=archive_size,width=20)
    with open(extract_path+filename,'wb') as f:
        def callback(chunk):
            f.write(chunk)
            archive_progress + len(chunk)
            archive_progress.show_progress()
        ftp.retrbinary("RETR " + prot_path,callback)
    archive_progress + archive_size
    archive_progress.show_progress()
    print()
    print ("download complete.")
    ftp.quit()
    print ("starting database upgrade...")
    subprocess.call(['./updater.sh'])

    
