import os
import progressbar
import sys
import domains_to_exons 
import sqlite3 as lite

transcript_db = 'db/transcript_data.db'
domains_db = 'db/domains.db'

def parse_gtf(file_path):
    with open(file_path) as f:
        lines = f.readlines()
    # dictionary of exons by transcript_id
    transcripts = {}
    transcript_id_prev = ''
    gene_id_prev = ''
    relative_end = 0
    exons = []
    for line in lines:
        splitted = line.split("\t")
        # check if feature is exon

        if splitted[2] == 'exon':
            exon = {}
            exon['gene_id'] = splitted[8].split('"')[1]
            exon['transcript_id'] = splitted[8].split('"')[3]
            exon['cds'] = {}
            exon['cds']['start'] = int(splitted[3])
            exon['cds']['end'] = int(splitted[4])
            exon['start'] = exon['cds']['start']
            exon['exon_starts'] = exon['cds']['start']
            exon['end'] = exon['cds']['end']
            exon['exon_ends'] = exon['cds']['end']
            exon['index'] = len(exons)
            # add one to the length
            exon['cds']['length'] = abs(exon['cds']['end'] - exon['cds']['start']) + 1
            # increment relative start location
            if exon['transcript_id'] == transcript_id_prev:
                relative_start = relative_end + 1
            # reset relative start location
            else:
                exons = []
                relative_start = 1

            relative_end = relative_start + exon['cds']['length']
            exon['relative_start'] = relative_start
            exon['relative_end'] = relative_end
            transcript_id_prev = exon['transcript_id']
            gene_id_prev = exon['gene_id']
            exons.append(exon)
            transcripts[exon['transcript_id']] = exons
    # maybe remove first element of transcripts
    # maybe not
    return transcripts

# checks if u_exon contains the exon inside itself
def exon_contained(u_exon,exon):
    if u_exon['start'] <= exon['start'] and u_exon['end'] >= exon['end']:
        return True
    return False

# exon is a dict with transcript_id and index
def get_exon_domains(exon):
    with lite.connect(domains_db) as con:
        cursor = con.cursor()
        cursor.execute("SELECT domains_list from domains WHERE transcript_id = ? AND exon_index = ?",(exon['transcript_id'],exon['index']))
        result = cursor.fetchone()
    #print('domains: {}'.format(result))
    if not result:


# usage: call when need to know what domains an exon contains
# takes transcript_data of user gtf file (cut up to dict)
# need to have atleast transcirpt_id and exons value
def assign_gtf_domains_to_exons(u_transcript_id, u_exons):
    exons = domains_to_exons.get_exons_by_transcript_id(u_transcript_id)
    # make sure there are exons
    if not exons:
        #print("failed assiging for t_id {}, no exons.".format(u_transcript_id))
        return None
    if not u_exons:
        #print("failed assiging for t_id {}, no u_exons.".format(u_transcript_id))
        return None
    # first extract all the domains so they are not extracted everytime
    exons_domains = list(map(get_exon_domains,exons))
    for u_exon in u_exons:
        # u_exons[domains] will be a set of strings
        u_exon['domains'] = set()
        for exon in exons:
            exon_domains = exons_domains[exon['index']]
            if exon_contained(u_exon,exon):
                u_exon['domains'].update(exon_domains)
                print(exon_domains)
                print(u_exon['domains'])
    # exons now have domains data
    for u_exon in u_exons:
        pass    #print(u_exon['domains'])
    return u_exons


# takes argv
def main():
    if len(sys.argv) < 3:
        print('inteface.py <inputfile> <outputfile>')
        sys.exit(2)
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    print('parsing {}...'.format(input_file))
    transcripts = parse_gtf(input_file)
    print('assigning domains to exons...')
    bar = progressbar.AnimatedProgressBar(end=len(transcripts),width=10)
    for transcript_id,exons in transcripts.items():
        transcripts[transcript_id] = assign_gtf_domains_to_exons(transcript_id,exons)
        bar+=1
        bar.show_progress()
    bar+=1
    bar.show_progress()
    to_write = [(name,data) for name,data in transcripts.items() if data]
    with open(output_file,'w') as f:
        for name,exons in to_write:
            f.write('{}:\n'.format(name))
            if not exons:
                f.write('None\n')
                continue
            for e in exons:
                f.write('index: {} domains: {}\n'.format(e['index'],str(e['domains'])))

    print()
    print('done')

if __name__ == '__main__':
    main()

