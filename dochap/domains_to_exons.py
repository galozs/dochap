import os
import sys
import json
import time
import dill
import sqlite3 as lite
import progressbar
from pathos.multiprocessing import ProcessingPool, ThreadingPool
from functools import partial
import conf

domains_db = 'db/domains.db'
alias_db = 'db/aliases.db'
comb_db = 'db/comb.db'
transcripts_db = 'db/transcript_data.db'
num_threads = 1
bar = 0
# TODO test and repair if needed
# run on all transcripts in transcripts.db
# for each one find matching alias in alias.db
# use alias to find sites and regions data in comb.db
# get all domains of all the variants of a given transcript (technicly of it's alias)
def get_domains(transcript_id, specie):
    with lite.connect(conf.databases[specie]) as con:
        cursor = con.cursor()
        cursor.execute("SELECT name from aliases WHERE transcript_id = ?",(transcript_id,))
        data = cursor.fetchall()
        if data:
            # create a list of the aliases
            aliases = list(set([tup[0] for tup in data]))
        else:
            return None
    with lite.connect(conf.databases[specie]) as con:
        list_of_domains_variants = []
        for alias in aliases:
            cursor = con.cursor()
            # there might be more then a single occurance of an alias in the genebank.
            # all occurances must be taken into account.
            cursor.execute("SELECT sites,regions from genebank WHERE symbol = ?",(alias,))
            results = cursor.fetchall()
            #print('result for {} alias {} is:\n{}'.format(transcript_id,alias,results))
            if results:
                domain_types = ['site','region']
                for variant_index,variant in enumerate(results):
                    domain_list = []
                    # if counter is 0, domain type is site, if counter is 1, domain type is region
                    for counter,domains in enumerate(variant):
                        splitted = domains.split(',')
                        #print ('splitted: ',splitted)
                        for result in splitted:
                            if '[' not in result or ']' not in result:
                                #print('bad result for {} alias {} result:\n'.format(transcript_id,alias,result))
                                continue
                            modified = result.replace(',',':')
                            part_one = '['.join(modified.split('[')[:-1])
                            part_two = modified.split('[')[-1].replace(']',':').split(':')
                            domain = {}
                            # check that line is not empty
                            #print ('modified: ',modified)
                            if not modified[0]:
                                #print('bad modified for {} alias {} modified:\n'.format(transcript_id,alias,modified))
                                continue
                            domain['type'] = domain_types[counter]
                            domain['name'] = part_one
                            if len(part_two) < 2:
                                print ('failed on part_two in function get_domains for transcript_id {} alias {}'.format(transcript_id, alias))
                                print ('result:', result)
                                print ('part_one: ',part_one)
                                print ('part_two: ',part_two)
                                print ('modified: ',modified)

                            domain['start'] = part_two[0]
                            domain['end'] = part_two[1]
                            domain['index'] = len(domain_list)
                            #print ('domain: ', domain)
                            if not str.isdigit(domain['start']) or not str.isdigit(domain['end']):
                                #print('bad strings in domain for {} alias {} domain:\n'.format(transcript_id,alias,domain))
                                continue
                            domain_list.append(domain)
                    # pack the information about the variant into a dictionary
                    #print('variant index: ',variant_index)      
                    info = {
                        'name':alias,
                        'variant_index':variant_index,
                        'domains':domain_list
                    }
                    list_of_domains_variants.append(info)
                    #print('found for {} alias {} doms list:\n{}'.format(transcript_id,alias,domain_list))
            else:
                pass
                #print('found no sites or regions for {} alias {}'.format(transcript_id,alias))

        #print('list_of_domains_variants for {} is: {}'.format(transcript_id,list_of_domains_variants))
        #print('number of variants for {} is: {}'.format(transcript_id,len(list_of_domains_variants)))
        return list_of_domains_variants

# input:
# transcript_id: string 
# specie: string of the specie (must be one from conf.py)
# output:
# list_of_exons_variants: list of dictionaries with exons variants, origin_id, and alias.
def get_exons_by_transcript_id_adv(transcript_id,specie):
    with lite.connect(conf.databases[specie]) as con:
        cursor = con.cursor()
        cursor.execute("SELECT name from aliases WHERE transcript_id = ?",(transcript_id,))
        data = cursor.fetchall()
        if data:
            # create a list of the aliases
            aliases = list(set([tup[0] for tup in data]))
        else:
            return None
    with lite.connect(conf.databases[specie]) as con:
        con.row_factory = lite.Row
        list_of_exons_variants = []
        for alias in aliases:
            cursor = con.cursor()
            # there might be more then a single occurance of an alias in the domains table.
            # all occurances must be taken into account.
            cursor.execute("SELECT * from domains WHERE gene_symbol = ?",(alias,))
            results = cursor.fetchall()
            if results:
                exons_variants_data = order_in_variants(results)
                #print('exons variants data for {}: {}'.format(transcript_id,exons_variants_data))
                list_of_exons_variants.append(
                            {
                            'origin_id':transcript_id,
                            'alias':alias,
                            'exons_variants_data':exons_variants_data
                            })
                #print(exons_variants_data)
        #print('list of exons variants for {} : {}'.format(transcript_id,list_of_exons_variants))
        return list_of_exons_variants
# order the query result into a dictionary by transcript_id
# and then by variant_name
# input:
# query_result: list of exons data from domains db.
# output:
# transcripts_dict: dictionary of transcripts variants with exons data.
def order_in_variants(query_result):
    transcripts_dict = {}
    # by transscript
    for result in query_result:
        #print('result in query result: {}'.format(dict(result)))
        transcript_id = result['transcript_id']
        variant_name = result['variant_name']
        if transcript_id not in transcripts_dict:
            transcripts_dict[transcript_id] = {}
        trans_dict = transcripts_dict[transcript_id]
        if variant_name not in trans_dict:
            trans_dict[variant_name] = []
        trans_dict[variant_name].append(dict(result))
    return transcripts_dict

def get_exons_by_transcript_id(transcript_id,specie):
    with lite.connect(conf.databases[specie]) as con:
        con.row_factory = lite.Row
        cursor = con.cursor()
        cursor.execute("SELECT * FROM transcripts WHERE name = ?",(transcript_id,))
        # currently use the first result only (there shouldnt be more then one)
        result = cursor.fetchone()
    exons = get_exons(result)
    return exons

def get_exons(result):
    if not result:
        #print('nothing in result')
        return
    exons =[]
    starts = result['exon_starts'].split(',')
    ends = result['exon_ends'].split(',')
    first_exon_start = int(starts[0])
    last_end = 0
    for i in range(int(result['exon_count'])):
        exon = {}
        exon['index'] = i
        exon['start'] = int(starts[i])
        exon['end'] = int(ends[i])
        exon['length'] = abs(exon['end'] - exon['start'])
        # the exon relative position
        exon['relative_start'] = last_end + 1
        exon['relative_end'] = last_end + 1 + exon['length']
        #exon['relative_start'] = abs(exon['start'] - first_exon_start) + 1
        #exon['relative_end'] = exon['relative_start'] + exon['length']
        last_end = exon['relative_end']
        exon['transcript_id'] = result['name']
        exons.append(exon)
    return exons


# input:
# transcript id: string
# variants_data: list of dictionary containing name,variant_index,domains
# specie: string of specie name from conf.py
# output:
# exons_variant_list - list of variant with exons data
def assignDomainsToExons(transcript_id, variants_data, specie):
    # get data about the transcript
        #print("exons",exons)
    #print("domains",domains)
    # TODO relative should be counted without spaces between exons
    # next statement might not be accurate
    # i dont know from what each domain relative location is relative to
    # domains indexes will be used as strings
    # states will be start,end,contains,contained
    # TODO CHANGED AND NOT TESTED - PROBABLY BREAKS
    if not variants_data:
        #print('variants_data for {} is empty'.format(transcript_id))
        return None
    exons_variant_list = []
    for variant in variants_data:
        with lite.connect(conf.databases[specie]) as con:
            con.row_factory = lite.Row
            cursor = con.cursor()
            cursor.execute("SELECT * FROM transcripts WHERE name = ?",(transcript_id,))
            # currently use the first result only (there shouldnt be more then one)
            result = cursor.fetchone()
        exons = get_exons(result)
        relative_start = 1
        relative_stop = 0
        last_exon = None
        for exon in exons:
            exon['domains_states'] = {}
            relative_stop = relative_start + exon['length']
            domains_in_exon = []
            domains = variant['domains']
            if domains == None:
                print('domains is empty')
                continue
            for domain in domains:
                if (not str.isdigit(domain['start'])):
                    print ("FAILED ON {} domain is: {}".format(transcript_id,domain))
                    sys.exit(2)
                dom_start = int(domain['start']) * 3 - 2
                dom_stop = int(domain['end']) * 3

                # create ranges of numbers that represents the domain and exon ranges
                if dom_start < dom_stop:
                    dom_range = range(dom_start,dom_stop+1)
                else:
                    dom_range = range(dom_stop,dom_start+1)

                exon_range = set(range(relative_start,relative_stop+1))
                intersection = exon_range.intersection(dom_range)
                #print('exon info: {} \nexon range: {}\n'.format(exon,range(relative_start,relative_stop+1)))
                #print('dom info: {}, dom range: {}\n'.format(domain,dom_range))
                #print('intersection: {}'.format(intersection))
                dom_start_in_exon = False
                dom_end_in_exon = False

                if not intersection:
                    # empty, no overlap
                    continue

                if dom_start in intersection:
                    # exon start location in domain
                    # domain is atleast partialy on exon
                    dom_start_in_exon = True

                if dom_stop in intersection:
                    # exon end location in domain
                    # domain is atleast partialy on exon
                    dom_end_in_exon = True

                dom_index = str(domain['index'])
                if dom_end_in_exon and dom_start_in_exon:
                    # domain fully in exon
                    exon['domains_states'][dom_index] = 'contained'
                    domains_in_exon.append(domain)
                    continue
                if dom_start_in_exon:
                    exon['domains_states'][dom_index] = 'start'
                    domains_in_exon.append(domain)
                    continue
                if dom_end_in_exon:
                    exon['domains_states'][dom_index] = 'end'
                    domains_in_exon.append(domain)
                    continue
                # there is an intersection but dom_start and dom_end not in it
                # that means that the domain contains the exon
                exon['domains_states'][dom_index] = 'contains'
                domains_in_exon.append(domain)
                continue

            nums = [domain['index'] for domain in domains_in_exon]
            exon['domains'] = domains_in_exon
            relative_start_mod = 0
            #if last_exon:
            #    relative_start_mod = abs(exon['start'] - last_exon['end'])
            relative_start = relative_stop + 1 + relative_start_mod
            last_exon = exon
        variant['exons'] = exons
        exons_variant_list.append(variant)
    #print('exons_variant_list: ',exons_variant_list)
    return exons_variant_list

def get_bar():
    return bar

def assign_and_get(specie,name):
    #print ('assign and get specie {} name {}'.format(specie,name))
    global bar
    bar = bar+1
    if name:
        return assignDomainsToExons(name,get_domains(name,specie),specie)
    return None

def write_to_db(data,specie):
    # write all domains in exons to db
    with lite.connect(conf.databases[specie]) as con:
        cursor = con.cursor()
        cursor.executescript("drop table if exists domains;")
        cursor.execute("CREATE TABLE domains(gene_symbol TEXT,variant_name TEXT, transcript_id TEXT, exon_index INT,exon_rel_start INT, exon_rel_end INT, domains_states TEXT, domains_list TEXT)")
        cursor.executemany("INSERT INTO domains VALUES(?,?,?,?,?,?,?,?)",data)



def main(specie):
    print("loading {} data...".format(specie))
    with lite.connect(conf.databases[specie]) as con:
        cursor = con.cursor()
        cursor.execute("SELECT DISTINCT transcript_id from aliases")
        result = cursor.fetchall()
    # TODO -  remve boundry fr names
    names = [value[0] for value in result][:1000]
    print("creating transcript database for {}".format(specie))
    # give this thing a progress bar
    global bar
    bar = progressbar.AnimatedProgressBar(end=len(names)+1,width=10)
    pool = ThreadingPool(num_threads)
    assign_and_get_with_specie = partial(assign_and_get, specie)
    result = pool.amap(assign_and_get_with_specie,names)
    while True:
        if result.ready():
            break
        bar.show_progress()
        time.sleep(1)
    data = list(result.get())
    #print(data)
    # dark magic incoming
    # flatten the list
    # make it a list of tuples of id,index,domainlist
    # TODO Change to deal with new variant data coming from assign_and_get 
    # variant has name,variant_index,domains,exons
    # TODO maybe no dark magic
    # TODO check that it is actually runs
    '''
    the following dark magic is one line of this:
    for variants in data:
        if not variants:
            continue
        for variant in variants:
            if not variant:
                continue
            for exon in variant['exons']:
                if not exon:
                    continue
            pass
    '''
    data = [
            (
            variant['name'],
            '_'.join([variant['name'],str(variant['variant_index'])]),\
            exon['transcript_id'],\
            exon['index'],\
            exon['relative_start'],\
            exon['relative_end'],\
            json.dumps(exon['domains_states']),\
            json.dumps(exon['domains'])\
            ) \
            for variants in data if variants != None \
            for variant in variants if variant != None \
            for exon in variant['exons'] if exon!= None
            ]
    print('new_data: \n',data)
#    print("well that was fun, now exit")
#    sys.exit(2)
    write_to_db(data,specie)
    print()
if __name__ == '__main__':
    for specie in conf.species:
        user_input = input("Create the {} domains database? (Y/n): ".format(specie))
        if user_input.lower() == 'n':
            continue
        main(specie)

