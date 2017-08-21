import sqlite3 as lite
import sys
import gbk_parser

records = gbk_parser.records

def create_aliases_db():
    # create database of aliases
    with lite.connect('db/aliases.db') as con:
        print ("Creating aliases database...")
        cur = con.cursor()
        cur.execute("CREATE TABLE genes(Id INT, symbol TEXT, aliases TEXT)")
        index=0
        with open("aliases.txt","r") as aliases_file:
            for gene_aliases in aliases_file.readlines():
                for aliase in gene_aliases.split(";"):
                    if aliase != "" and aliase !="\n":
                        cur.execute("INSERT INTO genes VALUES({0},'{1}','{2}')".format(index,aliase,gene_aliases))
                        index +=1
        print ("Aliases database created")

def create_comb_db():
    with lite.connect('db/comb.db') as con:
        print("Creating database...")
        cur = con.cursor()
        cur.execute("CREATE TABLE genes(Id INT, symbol TEXT,cds TEXT, sites TEXT, regions TEXT)")
        for index,record in enumerate(records):
            sites=[]
            regions=[]
            cds = []
            name =""
            for feature in record.features:
                if (feature.type == 'CDS'):
                    name=feature.qualifiers['gene'][0]
                    cds.append(feature.qualifiers['coded_by'][0] + str(feature.location))
                if (feature.type == 'Site'):
                    sites.append(feature.qualifiers['site_type'][0]+str(feature.location))
                if (feature.type == 'Region'):
                    regions.append(feature.qualifiers['region_name'][0]+str(feature.location))
            sites_comb = ','.join(sites)
            region_comb = ','.join(regions)
            cds_comb = ','.join(cds)
            if sites_comb == '' and sites_comb == '' and region_comb == '':
                continue
            cur.execute("INSERT INTO genes VALUES(?, ?, ?,?,?)",(index,name,cds_comb,sites_comb,region_comb))
            index+=1


if __name__ == "__main__":
    create_comb_db()
