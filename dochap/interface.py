import os
import json
import progressbar
import sys
import domains_to_exons
import sqlite3 as lite

transcript_db = 'db/transcript_data.db'
domains_db = 'db/domains.db'

def parse_gtf(file_path):
    with open(file_path) as f:
        lines = f.readlines()    # dictionary of exons by transcript_id
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
            exon['index'] = int(splitted[8].split('"')[5])
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


compare_stats = {'start':0,'end':0,'full':0,'partial':0,'none':0}
# checks if u_exon contains the exon inside itself
def compare_exons(u_exon,exon):
    # need to be changed massivly TODO
    # check for every domain inside exon
    domains_in_exon = []
    u_exon['domains_states'] = {}
    for domain in exon['domains']:
        # do same test as in domains_to_exon.py
        # just on actual location instead of relatives
        # TODO THIS MIGHT NOT MAKE SENSE - WHAT IS ADDED 
        # TO START OF DOMAIN? IS IT EXON?
        # MIGHT NEED TO ADD 1 TO START?
        total_start = int(domain['start']) + exon['start']
        total_end = int(domain['end']) + exon['end']
        dom_range = range(total_start,total_end+1)

        if u_exon['start'] > u_exon['end']:
            u_exon_range = set(range(u_exon['end'],u_exon['start']+1))
        else:
            u_exon_range = set(range(u_exon['start'],u_exon['end']+1))
        intersection = u_exon_range.intersection(dom_range)

        dom_start_in_exon = False
        dom_end_in_exon = False
        if not intersection:
            compare_stats['none']+=1
            continue

        if total_start in intersection:
            # exon start location in domain
            # domain is atleast partialy on exon
            dom_start_in_exon = True

        if total_end in intersection:
            # domain is atleast partialy on exon
            dom_end_in_exon = True

        # dom_index is string because its a key in domains_states dict
        dom_index = str(domain['index'])
        if dom_end_in_exon and dom_start_in_exon:
            compare_stats['full'] +=1
            u_exon['domains_states'][dom_index] = 'contained'
            domains_in_exon.append(domain)
            continue
        if dom_start_in_exon:
            compare_stats['start']+=1
            u_exon['domains_states'][dom_index] = 'start'
            domains_in_exon.append(domain)
            continue
        if dom_end_in_exon:
            compare_stats['end'] +=1
            u_exon['domains_states'][dom_index] = 'end'
            domains_in_exon.append(domain)
            continue
        compare_stats['partial']+=1
        u_exon['domains_states'][dom_index] = 'contains'
        domains_in_exon.append(domain)
        continue
    u_exon['domains'] = domains_in_exon
    if u_exon['domains_states'] == exon['domains_states']:
        if u_exon['domains'] == exon['domains']:
            u_exon['relation'] = 'identical'
        else:
            u_exon['relation'] = 'same domains states'
    else:
        u_exon['relation'] = 'different'

    # old way of comparison, should not be executed
    #print('\nu_exon: ', u_exon,'\nexon: ',exon)
    #print('u_exno is: {} exon is: {}'.format((u_exon['start'],u_exon['end']),(exon['start'],exon['end'])))
    #if u_exon['start']-1 <= exon['start']:
    #    pass#print('start is smaller')
    #if u_exon['end'] >= exon['end']:
    #    pass#print('end is larger')
    #if u_exon['start']-1 <= exon['start'] and u_exon['end'] >= exon['end']:
    #    return True
    #return False

# exon is a dict with transcript_id and index
def get_exon_domains(exon):
    with lite.connect(domains_db) as con:
        cursor = con.cursor()
        cursor.execute("SELECT domains_list from domains WHERE transcript_id = ? AND exon_index = ?",(exon['transcript_id'],exon['index']))
        result = cursor.fetchone()
    #print('domains: {}'.format(result))
    if not result:
       return None
    doms = result[0].split(',')
    return doms

def parse_exon_domains_to_dict(exons):
    for exon in exons:
        domains_string = exon['domains']#.replace("'",'"')
        #domains_string = '[{}]'.format(domains_string)
        domains_states_string = exon['domains_states']#.replace("'",'"')
        try:
            exon['domains'] = json.loads(domains_string)
            exon['domains_states'] = json.loads(domains_states_string)
        except :
            print("failed to load domains")
            print('dom: ',domains_string)
            print('dom_states: ',domains_states_string)
            sys.exit(2)

# call when exons list need to load domains info from domains table
def load_exons_domains(exons):
    transcript_id = exons[0]['transcript_id']
    indexes = set([str(exon['index']) for exon in exons])
    # conncet do domains db
    with lite.connect(domains_db) as con:
        cursor = con.cursor()
        cursor.execute("SELECT exon_index,domains_states,domains_list FROM domains WHERE transcript_id = ?",(transcript_id,))
        result = cursor.fetchall()
    # remember to check for None
    if not result:
        #print ('result is none:',result)
        return None
    values = {}
    for value in result:
        if value:
            # pack the domains_states and domains_list
            exons[int(value[0])]['domains_states'] = value[1]
            exons[int(value[0])]['domains'] = value[2]
            #print (exons[int(value[0])])
    parse_exon_domains_to_dict(exons)
    return True
# usage: call when need to know what domains an exon contains
# takes transcript_data of user gtf file (cut up to dict)
# need to have atleast transcirpt_id and exons value
def assign_gtf_domains_to_exons(u_transcript_id, u_exons):
    exons = domains_to_exons.get_exons_by_transcript_id(u_transcript_id)
    # make sure there are exons
    if not exons:
        #print("failed assiging for t_id {}, no exons.".format(u_transcript_id))
        return None
    # load the exons domains
    if not u_exons:
        #print("failed assiging for t_id {}, no u_exons.".format(u_transcript_id))
        return u_exons
    # first extract all the domains so they are not extracted everytime
    if not load_exons_domains(exons):
        # no domains for exons at all
        return u_exons
    #exons_domains = list(map(get_exon_domains,exons))
    #print('exons_doms: {}'.format(exons_domains))
    for u_exon in u_exons:
        # u_exons[domains] will be a set of strings
        for exon in exons:
            #exon_domains = exons_domains[exon['index']]
            compare_exons(u_exon,exon)
                # TODO domains assignments should be done in contain maybe
                # TODO or depend on string result
                # skip empty exons(no domains inside them)
                #if not exon_domains:
                # TODO DONE: COMPARISON IN compare_exons function
                #continue
                #u_exon['domains'].update(exon_domains)
                #print(exon_domains)
                #print(u_exon['domains'])
    # exons now have domains data
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
                doms = str(e.get('domains','no domains'))
                if doms != 'no_domains':
                    print("found one! {}.".format(e))
                states = str(e.get('domains_states','No states'))
                if doms == 'set()' or doms == "{''}" or doms == 'None':
                    e['domains'] = 'None'
                f.write('index: {} states: {} domains: {}\n'.format(e['index'],states,doms))

    print('stats:\n',compare_stats)
    print('done')

if __name__ == '__main__':
    main()

