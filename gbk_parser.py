import os
import threading
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.SeqFeature import SeqFeature, FeatureLocation
from Bio import SeqIO
import progressbar
# get all sequence records from the gbk file
gbk_file = "db/protein.gbk"
#records = [record for record in SeqIO.parse(gbk_file,"genbank")]
print ("parsing protein.gbk")
records=[]
# length as of 2016
length = 76216
p_bar = progressbar.AnimatedProgressBar(end=length,width=100)
p_bar+1
for record in SeqIO.parse(gbk_file,"genbank"):
    records.append(record)
    p_bar+1
    p_bar.show_progress()
p_bar+length

# number of sequence records extracted
print (len(records))
def write_annotations():
    print ("writing annotation.txt")
    with open("annotation.txt","w") as annotations_file:
        for record in records:
            annotations_file.write(str(record))


def write_cds():
    print ("writing cds.txt")
    with open("cds.txt","w") as cds_file:
        for record in records:
            features = [feature for feature in record.features if feature.type == "CDS"]
            for feature in features:
                cds_file.write(str(feature))

def write_sites():
    print("writing sites.txt")
    with open("sites.txt","w") as sites_file:
        for record in records:
            features = [feature for feature in record.features if feature.type== "Site"]
            for feature in features:
                sites_file.write(str(feature))
                # can take begin@end@name maybe
def write_regions():
    print("writing regions.txt")
    with open("regions.txt","w") as regions_file:
        for record in records:
            features = [feature for feature in record.features if feature.type == "Region"]
            for feature in features:
                regions_file.write(str(feature))

def write_aliases():
    print("writing aliases.txt")
    with open("aliases.txt","w") as aliases_file:
        aliases = set()
        for record in records:
            features = [feature for feature in record.features if feature.type == "CDS"]
            for feature in features:
                gene_aliases =""
                gene_name =""
                if "gene" in feature.qualifiers:
                    gene_name = feature.qualifiers["gene"][0]
                if "gene_synonym" in feature.qualifiers:
                    gene_aliases = feature.qualifiers["gene_synonym"][0]
                if gene_name:
                    aliases.add(gene_name + ";" + gene_aliases)
        for aliase in aliases:
            aliases_file.write(aliase +"\n")
if __name__ == "__main__":
    threads = []
    t_1 = threading.Thread(target=write_annotations)
    threads.append(t_1)
    t_1.start()
    t_2 = threading.Thread(target=write_aliases)
    threads.append(t_2)
    t_2.start()
    t_3 = threading.Thread(target=write_sites)
    threads.append(t_3)
    t_3.start()
    t_4 = threading.Thread(target=write_regions)
    threads.append(t_4)
    t_4.start() 
