import sqlite3 as lite
import sys

with lite.connect('test.db') as con:
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
