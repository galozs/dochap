from ftplib import FTP
import tarfile
prot_path = "genomes/Mus_musculus/protein/protein.gbk.gz"
filename = "protein.gbk.gz"
extract_path = "db/"
print ("connecting to ftp.ncbi.nlm.nih.gov...")
ftp = FTP("ftp.ncbi.nlm.nih.gov")
print ("logging in...")
ftp.login()
print ("downloading " + filename + "...")
ftp.retrbinary("RETR " + prot_path,open(filename,'wb').write)
print ("download complete.")
ftp.quit()
