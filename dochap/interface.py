import os
import json
import progressbar
import sys
import domains_to_exons
import sqlite3 as lite
import conf

transcript_db = 'db/transcript_data.db'
domains_db = 'db/domains.db'

# RELATIVE CALCULATIONS ARE PROBABLY WRONG
# MIGHT NEED TO GO BY TOTAL POSTITIONS OR
# FIND A WAY TO HAVE CORRECT RELATIVE POSTITIONS
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
                # SHOULD BE relative_start = relative_end + ({NEW EXON START} - {LAST EXON START})
                relative_start = relative_end + 1 + abs(last_exon['end'] - exon['start'])
            # reset relative start location
            else:
                exons = []
                relative_start = 1

            relative_end = relative_start + exon['cds']['length']
            exon['relative_start'] = relative_start
            exon['relative_end'] = relative_end
            last_exon = exon
            transcript_id_prev = exon['transcript_id']
            gene_id_prev = exon['gene_id']
            exons.append(exon)
            transcripts[exon['transcript_id']] = exons
        # maybe remove first element of transcripts
    # maybe not
    return transcripts


# compare the domains of user exon and db exon
# 
def compare_domains(u_exon,exon):
    if u_exon['start'] == exon['start'] and u_exon['end'] == exon['end']:
                return 'identical'
    if u_exon['domains_states'] == exon['domains_states']:
        if u_exon['domains'] == exon['domains']:
                return 'domains match'
        return 'domains_states match'
    return 'different'

# check how u_exon compares to the database exons
def compare_exons(u_exon,exons):
    # TODO - decide what should be the compare function
    u_exon['relations'] = []
    for exon in exons:
        u_exon['relations'].append(compare_domains(u_exon,exon))


# returns the domains associated with a given exon index and transcript id 
# input:
# exon: dict with transcript_id and index
# specie: string of the specie (must be one from conf.py)
def get_exon_domains(exon,specie):
    with lite.connect(conf.databases[specie]) as con:
        cursor = con.cursor()
        cursor.execute("SELECT domains_list from domains WHERE transcript_id = ? AND exon_index = ?",(exon['transcript_id'],exon['index']))
        result = cursor.fetchone()
    if not result:
       return None
    doms = result[0].split(',')
    return doms

# parse the given exons json string
# input:
# exons: list of dictionaries that contains json dump of domains and domains_states
# output:
# exons: list of dictionaris that contains domains and domains_states
def parse_exon_domains_to_dict(exons):
    for exon in exons:
        domains_string = exon['domains']#.replace("'",'"')
        domains_states_string = exon['domains_states']#.replace("'",'"')
        try:
            exon['domains'] = json.loads(domains_string)
            exon['domains_states'] = json.loads(domains_states_string)
        except :
            print("failed to load domains")
            print('dom: ',domains_string)
            print('dom_states: ',domains_states_string)
            sys.exit(2)
    return exons

# call when exons list need to load domains info from domains table
# input:
# exons: list of dictionaries that will be populated with json strings from the database
# specie: string of the specie (must be one from conf.py)
# output:
# True if loaded anything
# None if didn't load anything
def load_exons_domains(exons,specie):
    transcript_id = exons[0]['transcript_id']
    indexes = set([str(exon['index']) for exon in exons])
    # conncet do domains db
    with lite.connect(conf.databases[specie]) as con:
        cursor = con.cursor()
        cursor.execute("SELECT exon_index,domains_states,domains_list FROM domains WHERE transcript_id = ?",(transcript_id,))
        result = cursor.fetchall()
    # remember to check for None
    if not result:
        #print ('result is none:',result)
        return None
    for value in result:
        if value:
            # pack the domains_states and domains_list
            exons[int(value[0])]['domains_states'] = value[1]
            exons[int(value[0])]['domains'] = value[2]
            #print (exons[int(value[0])])
    parse_exon_domains_to_dict(exons)
    return True


# TODO if comparison method is changed - update this method.
# usage: call to fill exon with domain data
# input:
# exon: dictionary of exon data
# domains: list of domains (dictionaries)
# output:
# the exon's key domains_states will be a list of states (index will reference the domain's index)
# possible values: 'contained','start','end','contained'.
def assign_domains_to_exon(exon, domains):
    domains_in_exon = []
    exon['domains_states'] = {}
    for domain in domains:
        # do same test as in domains_to_exon.py
        dom_start = int(domain['start']) * 3 -2
        dom_end = int(domain['end']) * 3
        dom_range = range(dom_start,dom_end+1)
        exon_range = set(range(exon['relative_start'],exon['relative_end']))
        intersection = exon_range.intersection(dom_range)
        dom_start_in_exon = False
        dom_end_in_exon = False
        if not intersection:
            continue
        if dom_start in intersection:
            dom_start_in_exon = True
        if dom_end in intersection:
            dom_end_in_exon = True
        dom_index_string = str(domain['index'])
        if dom_end_in_exon and dom_start_in_exon:
            exon['domains_states'][dom_index_string] = 'contained'
            domains_in_exon.append(domain)
            continue
        if dom_start_in_exon:
            exon['domains_states'][dom_index_string] = 'start'
            domains_in_exon.append(domain)
            continue
        if dom_end_in_exon:
            exon['domains_states'][dom_index_string] = 'end'
            domains_in_exon.append(domain)
            continue
        exon['domains_states'][dom_index_string] = 'contains'
        domains_in_exon.append(domain)
        continue
    exon['domains'] = domains_in_exon

# usage: call when need to know what domains an exon contains
# takes transcript_data of user gtf file (cut up to dict)
# need to have atleast transcirpt_id and exons value
# input:
# u_transcript_id:  id of the transcript
# u_exons: list of dictionaries
# specie: string of the specie (must be one from conf.py)
# output:
# u_exons: the exons of the transcript id
# domains: the domains of the transcript id
def assign_gtf_domains_to_exons(u_transcript_id, u_exons,specie):
    domains = domains_to_exons.get_domains(u_transcript_id,specie)
    #print ('possible domains: ',domains)
    # check for failure
    if not domains or not u_exons:
        return u_exons, domains
    # for each u_exon, check every domain
    for u_exon in u_exons:
        assign_domains_to_exon(u_exon,domains)
    # can now do compare to exons step

    exons = domains_to_exons.get_exons_by_transcript_id(u_transcript_id,specie)
    # make sure there are exons
    if not exons:
        return u_exons, domains
    # load the exons domains
    # first extract all the domains so they are not extracted everytime
    if not load_exons_domains(exons,specie):
        # no domains for exons at all
        return u_exons, domains
    #exons_domains = list(map(get_exon_domains,exons,specie))
    #print('exons_doms: {}'.format(exons_domains))
    #for u_exon in u_exons:
        # u_exons[domains] will be a set of strings
        #compare_exons(u_exon,exons)
    return u_exons, domains
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

# the interface of dochap.
# input:
# input_file: path to input file
# output_file: path to the output file
# specie: string of the specie (must be one from conf.py)
# output:
# output_file: the path to the output file
def interface(input_file,output_file,specie):
    print('parsing {}...'.format(input_file))
    transcripts = parse_gtf(input_file)
    print('assigning domains to exons...')
    bar = progressbar.AnimatedProgressBar(end=len(transcripts),width=10)
    for transcript_id,exons in transcripts.items():
        transcripts[transcript_id] = assign_gtf_domains_to_exons(transcript_id,exons,specie)
        bar+=1
        bar.show_progress()
    bar+=1
    bar.show_progress()
    to_write = [(name,data) for name,data in transcripts.items() if data]
    with open(output_file,'w') as f:
        f.write(json.dumps(transcripts))
    # stop here
    return output_file


# takes argv
# usage - will be printed upon calling the script
def main():
    if len(sys.argv) < 4:
        print('inteface.py <specie> <inputfile> <outputfile>')
        sys.exit(2)
    specie = sys.argv[1]
    input_file = sys.argv[2]
    output_file = sys.argv[3]
    print('parsing {}...'.format(input_file))
    transcripts = parse_gtf(input_file)
    print('assigning domains to exons...')
    bar = progressbar.AnimatedProgressBar(end=len(transcripts),width=10)
    for transcript_id,exons in transcripts.items():
        transcripts[transcript_id] = assign_gtf_domains_to_exons(transcript_id,exons,specie)
        bar+=1
        bar.show_progress()
    bar+=1
    bar.show_progress()
    to_write = [(name,data) for name,data in transcripts.items() if data]
    with open(output_file,'w') as f:
        f.write(json.dumps(transcripts))
    # stop here
    return
    with open(output_file,'w') as f:
        for name,exons in to_write:
            f.write('{}:\n'.format(name))
            if not exons:
                f.write('None\n')
                continue
            for e in exons:
                doms = str(e.get('domains','[]'))
                states = str(e.get('domains_states','{}'))
                loc = str((e.get('start',None),e.get('end',None)))
                rel_loc = str((e.get('relative_start',None),e.get('relative_end',None)))
                f.write('index: {} loc: {}, rel_loc: {} states:{} domains: {}\n'.format(e['index'],loc,rel_loc,states,doms))
    print('done')

if __name__ == '__main__':
    main()

