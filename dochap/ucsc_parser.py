import os
import conf

knownGene_path = 'db/{}/knownGene.txt'
# parse a given knownGene table from ucsc
# returns a nice dictionary
def parse_knownGene(path):
    # find file
    with open(path,'r') as f:
        lines = f.readlines()
    names = {}
    for line in lines:
        line = line.replace('\n','').replace('\\n','')
        splitted_line = line.split('\\t')
        if len(splitted_line) <2:
            splitted_line = line.split('\t')
        data = {}
        data['name'] = splitted_line[0]
        data['chrom'] = splitted_line[1]
        data['strand'] = splitted_line[2]
        data['tx_start'] = splitted_line[3]
        data['tx_end'] = splitted_line[4]
        data['cds_start'] = splitted_line[5]
        data['cds_end'] = splitted_line[6]
        data['exon_count'] = splitted_line[7]
        data['exon_starts'] = splitted_line[8]
        data['exon_ends'] = splitted_line[9]
        data['protein_id'] = splitted_line[10]
        data['align_id'] = splitted_line[11]
        names[data['name']] = data
    return names

def main():
    for specie in conf.species:
        parse_knownGene(knownGene_path.format(specie))

if __name__ == '__main__':
    main()

