import os
import sqlite3 as lite

alias_db = 'db/aliases.db'
comb_db = 'db/comb.db'
transcripts_db = 'db/transcript_data.db'


# run on all transcripts in transcripts.db
# for each one find matching alias in alias.db
# use alias to find sites and regions data in comb.db
def getDomains(transcript_id):
    with lite.connect(alias_db) as con:
        cursor = con.cursor()
        cursor.execute("SELECT aliases from genes WHERE transcript_id = ?",(transcript_id,))
        data = cursor.fetchone()
        if data:
            aliases = data[0].split(';')
        else:
            return None
    with lite.connect(comb_db) as con:
        for alias in aliases:
            cursor = con.cursor()
            cursor.execute("SELECT sites,regions from genes WHERE symbol = ?",(alias,))
            results = cursor.fetchall()
            domain_list = []
            if results:
                for domains in results[0]:
                    splitted = domains.split(',')
                    for result in splitted:
                        modified = result.replace('[',':').replace(']',':').replace(',',':').split(':')
                        domain = {}
                        # check that line is not empty
                        if not modified[0]:
                            continue
                        domain['name'] = modified[0]
                        domain['start'] = modified[1]
                        domain['end'] = modified[2]
                        domain['index'] = len(domain_list)
                        domain_list.append(domain)
                return domain_list

def main():
    print(getDomains('uc007aeu.1'))
    print(getDomains('uc012gqd.1'))
    print(getDomains('uc007afi.2'))


if __name__ == '__main__':
    main()

