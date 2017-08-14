from ftplib import FTP
import tarfile
import os.path
import subprocess
prot_path = "genomes/Mus_musculus/protein/protein.gbk.gz"
filename = "protein.gbk.gz"
extract_path = "db/"
readme_file = 'genomes/Mus_musculus/README_CURRENT_RELEASE'
print ("connecting to ftp.ncbi.nlm.nih.gov...")
ftp = FTP("ftp.ncbi.nlm.nih.gov")
print ("logging in...")
ftp.login()
print ("downloading readme_file...")
ftp.retrlines("RETR " + readme_file,open(extract_path+"readme_new","w").write)
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
    ftp.retrbinary("RETR " + prot_path,open(extract_path+filename,'wb').write)
    print ("download complete.")
    ftp.quit()
    print ("starting database upgrade...")
    subprocess.call(['./updater.sh'])

    
