import Bio

from Bio import SeqIO
with open("test.txt",'w') as fout:
    for seq_record in SeqIO.parse("db/protein.gbk","genbank"):
        sequence = seq_record.seq
        fout.write(str(sequence) + "\n")   
