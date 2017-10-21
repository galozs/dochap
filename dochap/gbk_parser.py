import os
import threading
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.SeqFeature import SeqFeature, FeatureLocation
from Bio import SeqIO
import progressbar
import conf
from functools import partial



gbk_file = "db/{}/protein.gbk"


def get_records():
    """
     get all sequence records from the gbk file
    """
    records = {specie:parse_proteins(specie) for specie in conf.species}
    return records

def parse_proteins(specie):
    """
    records = [record for record in SeqIO.parse(gbk_file,"genbank")]
    """
    print ("parsing protein.gbk of {}".format(specie))
    records=[]
    # length as of 2016 of mouse
    length = 76216
    p_bar = progressbar.AnimatedProgressBar(end=length,width=10)
    p_bar+1
    for record in SeqIO.parse(gbk_file.format(specie),"genbank"):
        records.append(record)
        p_bar+1
        p_bar.show_progress()
    print()
    print("done")
    return records
def write_annotations(specie):
    """
    """
    print ("writing annotation.txt")
    with open("annotation.txt","w") as annotations_file:
        for record in records[specie]:
            annotations_file.write(str(record))

def write_cds(specie):
    """
    """
    print ("writing cds.txt")
    with open("cds.txt","w") as cds_file:
        for record in records[specie]:
            features = [feature for feature in record.features if feature.type == "CDS"]
            for feature in features:
                cds_file.write(str(feature))
def write_sites(specie):
    """
    """
    print("writing sites.txt")
    with open("sites.txt","w") as sites_file:
        for record in records[specie]:
            features = [feature for feature in record.features if feature.type== "Site"]
            for feature in features:
                sites_file.write(str(feature))
                # can take begin@end@name maybe
def write_regions(specie):
    """
    """
    print("writing regions.txt")
    with open("regions.txt","w") as regions_file:
        for record in records[specie]:
            features = [feature for feature in record.features if feature.type == "Region"]
            for feature in features:
                regions_file.write(str(feature))
def write_aliases(specie):
    """
    """
    print("writing aliases.txt")
    with open("aliases.txt","w") as aliases_file:
        aliases = set()
        for record in records[specie]:
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
    for specie in conf.species:
        func = partial(write_aliases,specie)
        t = threading.Thread(target=func)
        t.start()
