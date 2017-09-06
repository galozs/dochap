import os
import domains_to_exons
import sqlite3 as lite

transcript_db = 'db/transcript_data.db'
domains_db = 'db/domains.db'

def main():
    pass

def parse_gtf(file_path):
    with open(file_path) as f:
        lines = f.readlines()
    # dictionary of exons by transcript_id
    transcript = {}
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
        cursor con.cursor()
        cursor.execute("SELECT domains from domains WHERE transcript_id = ? and index = ?",(exon['transcript_id'],exon['index']))
        result = cursor.fetchall()
    print('get exon {} domains: {}'.format(exon,result))
    return result[0].split(',')


# usage: call when need to know what domains an exon contains
# takes transcript_data of user gtf file (cut up to dict)
# need to have atleast transcirpt_id and exons value
def assign_gtf_domains_to_exons(u_transcript_id, u_exons):
    exons = domains_to_exons.get_exons_by_transcript_id(u_transcript_id)
    # make sure there are exons
    if not exons or not u_exons:
        print("failed assiging for t_id {}, no exons.".format(u_transcript_id))

    for u_exon in u_exons:
        # u_exons[domains] will be a set of strings
        u_exon['domains'] = set()
        for exon in exons:
            exon_domains = get_exon_domains(exon)
                if exon_contained(u_exon,exon):
                    u_exon['domains'].update(exon_domains)
    # u_transcript_data now have domains data in exons dicts
    return u_transcript_data

if __name__ == '__main__':
    main()

