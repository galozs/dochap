import os
import time
import dill
import sqlite3 as lite
import progressbar
from pathos.multiprocessing import ProcessingPool, ThreadingPool
from functools import partial

domains_db = 'db/domains.db'
alias_db = 'db/aliases.db'
comb_db = 'db/comb.db'
transcripts_db = 'db/transcript_data.db'
num_threads = 8
bar = 0
# run on all transcripts in transcripts.db
# for each one find matching alias in alias.db
# use alias to find sites and regions data in comb.db
# get all domains of a transcript
def get_domains(transcript_id):
    # use better aliases
    alias_db = 'db/better_aliases.db'
    with lite.connect(alias_db) as con:
        cursor = con.cursor()
        cursor.execute("SELECT name from aliases WHERE transcript_id = ?",(transcript_id,))
        #cursor.execute("SELECT aliases from genes WHERE transcript_id = ?",(transcript_id,))
        data = cursor.fetchall()
        if data:
            # create a list of the aliases
            aliases = list(set([tup[0] for tup in data]))
            #aliases = data[0].split(';')
        else:
            return None
    with lite.connect(comb_db) as con:
        for alias in aliases:
            cursor = con.cursor()
            cursor.execute("SELECT sites,regions from genes WHERE symbol = ?",(alias,))
            results = cursor.fetchall()
            domain_list = []
            #print('result for {} alias {} is:\n{}'.format(transcript_id,alias,results))
            if results:
                for domains in results[0]:
                    splitted = domains.split(',')
                    for result in splitted:
                        if '[' not in result:
                            #print('bad result for {} alias {} result:\n'.format(transcript_id,alias,result))
                            continue
                        modified = result.replace(',',':')
                        part_one = '['.join(modified.split('[')[:-1])
                        part_two = modified.split('[')[-1].replace(']',':').split(':')
                        domain = {}
                        # check that line is not empty
                        if not modified[0]:
                            #print('bad modified for {} alias {} modified:\n'.format(transcript_id,alias,modified))
                            continue
                        domain['name'] = part_one
                        domain['start'] = part_two[0]
                        domain['end'] = part_two[1]
                        domain['index'] = len(domain_list)
                        if not str.isdigit(domain['start']) or not str.isdigit(domain['end']):
                            #print('bad strings in domain for {} alias {} domain:\n'.format(transcript_id,alias,domain))
                            continue
                        domain_list.append(domain)
                #print('found for {} alias {} doms list:\n{}'.format(transcript_id,alias,domain_list))
                return domain_list
            else:
                pass
                #print('found no sites or regions for {} alias {}'.format(transcript_id,alias))

def get_exons_by_transcript_id(transcript_id):
    with lite.connect(transcripts_db) as con:
        con.row_factory = lite.Row
        cursor = con.cursor()
        cursor.execute("SELECT * FROM transcripts WHERE name = ?",(transcript_id,))
        # currently use the first result only (there shouldnt be more then one)
        result = cursor.fetchone()
    exons = get_exons(result)
    return exons

def get_exons(result):
    exons =[]
    starts = result['exon_starts'].split(',')
    ends = result['exon_ends'].split(',')
    for i in range(int(result['exon_count'])):
        exon = {}
        exon['index'] = i
        exon['start'] = int(starts[i])
        exon['end'] = int(ends[i])
        exon['length'] = exon['end'] - exon['start']
        exon['transcript_id'] = result['name']
        exons.append(exon)
    return exons


def assignDomainsToExons(transcript_id,domains):
    # get data about the transcript
    with lite.connect(transcripts_db) as con:
        con.row_factory = lite.Row
        cursor = con.cursor()
        cursor.execute("SELECT * FROM transcripts WHERE name = ?",(transcript_id,))
        # currently use the first result only (there shouldnt be more then one)
        result = cursor.fetchone()
    exons = get_exons(result)
    relative_start = 1
    relative_stop = 0
    for exon in exons:
        relative_stop = relative_start + exon['length']
        domains_in_exon = []
        if domains == None:
            return
        for domain in domains:
            if (not str.isdigit(domain['start'])):
                #print ("FUCKING FAILED ON {} domain is: {}".format(transcript_id,domain))
                sys.exit(2)
            dom_start = int(domain['start']) * 3 - 2
            dom_stop = int(domain['end']) * 3
            #print('start {} end {}'.format(dom_start,dom_stop))
            #print ('relative start {} relative end {}'.format(relative_start,relative_stop))
            dom_start_in = relative_start <= dom_start and dom_start <= relative_stop
            dom_end_in = relative_start <= dom_stop and dom_stop <= relative_stop
            if dom_start_in or dom_end_in:
                domains_in_exon.append(domain)
        nums = [domain['index'] for domain in domains_in_exon]
        exon['domains'] = nums
        relative_start = relative_stop + 1
    return exons

def get_bar():
    return bar

def assign_and_get(name):
    global bar
    bar = bar+1
    if name:
        return assignDomainsToExons(name,get_domains(name))
    return None

def write_to_db(data):
    # write all domains in exons to db
    # data is build [(id,index,[domains_nums]),...]
    #print('writing to db/domains.db...')
    with lite.connect(domains_db) as con:
        cursor = con.cursor()
        cursor.executescript("drop table if exists domains;")
        cursor.execute("CREATE TABLE domains(transcript_id TEXT, exon_index INT, domains_list TEXT)")
        cursor.executemany("INSERT INTO domains VALUES(?,?,?)",data)



def main():
    #print(get_domains('uc007aeu.1'))
    #print(get_domains('uc012gqd.1'))
    #print(get_domains('uc007afi.2'))
    print("loading data...")
    with lite.connect('db/better_aliases.db') as con:
        cursor = con.cursor()
        cursor.execute("SELECT DISTINCT transcript_id from aliases")
        result = cursor.fetchall()
    names = [value[0] for value in result]
    # give this thing a progress bar
    global bar
    bar = progressbar.AnimatedProgressBar(end=len(names),width=10)
    pool = ThreadingPool(num_threads)
    result = pool.amap(assign_and_get,names)
    while True:
        if result.ready():
            break
        bar.show_progress()
        time.sleep(1)
    data = list(result.get())
    # dark magic incoming
    # flatten the list
    # make it a list of tuples of id,index,domainlist
    data = [(exon['transcript_id'],exon['index'],','.join((list(map(str,exon['domains']))))) for exons in data if exons != None for exon in exons if exon != None]
    #ids = [tup[0] for tup in data]
    #indexes = [tup[1] for tup in data]
    #domains = [tup[2] for tup in data]
    #data = zip(ids,indexes,names)
    write_to_db(data)

if __name__ == '__main__':
    main()

