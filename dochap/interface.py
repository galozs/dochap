import os
import json
import progressbar
import sys
import domains_to_exons import sqlite3 as lite import conf
import new_visualizer

transcript_db = 'db/transcript_data.db'
domains_db = 'db/domains.db'

def parse_gtf(file_path):
    """
    # RELATIVE CALCULATIONS ARE PROBABLY WRONG
    # MIGHT NEED TO GO BY TOTAL POSTITIONS OR
    # FIND A WAY TO HAVE CORRECT RELATIVE POSTITIONS
    """
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
            transcripts[exon['transcript_id']] = {'exons':exons}
        # maybe remove first element of transcripts
    # maybe not
    return transcripts


def compare_domains(u_exon,exon):
    """
     compare the domains of user exon and db exon
    """
    if u_exon['start'] == exon['start'] and u_exon['end'] == exon['end']:
                return 'identical'
    if u_exon['domains_states'] == exon['domains_states']:
        if u_exon['domains'] == exon['domains']:
                return 'domains match'
        return 'domains_states match'
    return 'different'
def compare_exons(u_exon,exons):
    """
     check how u_exon compares to the database exons
    """
    # TODO - decide what should be the compare function
    u_exon['relations'] = []
    for exon in exons:
        u_exon['relations'].append(compare_domains(u_exon,exon))


def get_exon_domains(exon,specie):
    """
     returns the domains associated with a given exon index and transcript id 
     input:
     exon: dict with transcript_id and index
     specie: string of the specie (must be one from conf.py)
    """
    with lite.connect(conf.databases[specie]) as con:
        cursor = con.cursor()
        cursor.execute("SELECT domains_list from domains WHERE transcript_id = ? AND exon_index = ?",(exon['transcript_id'],exon['index']))
        result = cursor.fetchone()
    if not result:
       return None
    doms = result[0].split(',')
    return doms

def parse_exon_domains_to_dict(exons):
    """
     parse the given exons json string
     input:
     exons: list of dictionaries that contains json dump of domains and domains_states
     output:
     exons: list of dictionaris that contains domains and domains_states
    """
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

def load_exons_domains(exons,specie):
    """
     call when exons list need to load domains info from domains table
     input:
     exons: list of dictionaries that will be populated with json strings from the database
     specie: string of the specie (must be one from conf.py)
     output:
     True if loaded anything
     None if didn't load anything
    """
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


def assign_domains_to_exon(exon, domains):
    """
     TODO if comparison method is changed - update this method.
     usage: call to fill exon with domain data
     input:
     exon: dictionary of exon data
     domains: list of domains (dictionaries)
     output:
     the exon's key domains_states will be a list of states (index will reference the domain's index)
     possible values: 'contained','start','end','contained'.
    """
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

def assign_gtf_domains_to_exons(u_transcript_id, u_exons,specie):
    """
     usage: call when need to know what domains an exon contains
     takes transcript_data of user gtf file (cut up to dict)
     need to have atleast transcirpt_id and exons value
     input:
     u_transcript_id:  id of the transcript
     u_exons: list of dictionaries containing user exons data
     specie: string of the specie (must be one from conf.py)
     output:
     list_of_variants: list of the variants with exons and domains data
     exons_variants_list: exons data from the database about all the possible related exons to the user transcript
    """
    list_of_variants= domains_to_exons.get_domains(u_transcript_id,specie)
    # check for failure
    if not list_of_variants or not u_exons:
        return u_exons, list_of_variants
    # for each u_exon, check every domain
    for variant in list_of_variants:
        domains = variant['domains']
        copy_u_exons = list(u_exons)
        for u_exon in copy_u_exons:
            assign_domains_to_exon(u_exon,domains)
        variant['u_exons'] = list(copy_u_exons)

    exons_variants_list = domains_to_exons.get_exons_by_transcript_id_adv(u_transcript_id,specie)
    # make sure there are exons
    if not exons_variants_list:
        return None
    return list_of_variants, exons_variants_list

def get_domains_in_transcript(transcript_id,specie):
    """
    get all domains variations in a given transcript.

    input:
        transcript_id: string
        specie: string of the specie (must be one from conf.py)
    output:
        dictionary: keys are aliases of the transcript_id, values are lists of domains
    """
    # query aliases table to get aliases for transcript_id
    domain_types = ['site','region']
    with lite.connect(conf.databases[specie]) as con:
        cursor = con.cursor()
        cursor.execute("SELECT name FROM aliases WHERE transcript_id = ?",(transcript_id,))
        aliases = list(set([tup[0] for tup in cursor.fetchall()]))
        alias_domains_dict = {}
        for alias in aliases:
            cursor.execute("SELECT regions,sites FROM genebank WHERE symbol = ?",(alias,))
            results = cursor.fetchall()
            variants = []
            for variant in results:
                domain_list = []
                # if counter is 0, domain type is site, if counter is 1, domain type is region
                for counter,domains in enumerate(variant):
                    splitted = domains.split(',')
                    #print ('splitted: ',splitted)
                    for result in splitted:
                        if '[' not in result or ']' not in result:
                            continue
                        modified = result.replace(',',':')
                        part_one = '['.join(modified.split('[')[:-1])
                        part_two = modified.split('[')[-1].replace(']',':').split(':')
                        domain = {}
                        # check that line is not empty
                        if not modified[0]:
                            continue
                        domain['type'] = domain_types[counter]
                        domain['name'] = part_one
                        if len(part_two) < 2:
                            print('fail part_two')
                            continue
                        domain['start'] = part_two[0]
                        domain['end'] = part_two[1]
                        domain['index'] = len(domain_list)
                        # check that domain start and end are numbers
                        if not str.isdigit(domain['start']) or not str.isdigit(domain['end']):
                            continue
                        domain_list.append(domain)
               if domains_list:
                   variants.append(domains_list)

            if variants:
                alias_domains_dict[alias] = variants

        return alias_domains_dict

def interface(input_file,specie):
    """
     the interface of dochap.
     input:
         input_file: path to input file
         specie: string of the specie (must be one from conf.py)
    """
    print('parsing {}...'.format(input_file))
    transcripts = parse_gtf(input_file)
    print('assigning domains to exons...')
    bar = progressbar.AnimatedProgressBar(end=len(transcripts),width=10)
    for transcript_id in transcripts:
        transcripts[transcript_id]['domains'] = get_domains_in_transcript(transcript_id,specie)
        bar+=1
        bar.show_progress()
    bar+=1
    bar.show_progress()
    to_write = [(name,data) for name,data in transcripts.items() if data]
    new_visualizer.visualize(transcripts)
    # stop here


def main():
    """
     takes argv
     usage - will be printed upon calling the script
    """
    if len(sys.argv) < 3:
        print('inteface.py <specie> <inputfile>')
        sys.exit(2)
    specie = sys.argv[1]
    input_file = sys.argv[2]
    interface(input_file,specie)
    return

if __name__ == '__main__':
    main()

