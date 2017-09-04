import os
import requests

url = "http://genome-euro.ucsc.edu/cgi-bin/hgTables"
session = requests.Session()

params2 = {
    'hgsid':'605922159_gOUJ14QP9JLMQLftQOx39ehhfaNQ',
    'jsh_pageVertPos': '0',
    'clade': 'mammal',
    'org': 'Mouse',
    'db': 'mm10',
    'hgta_group': 'genes',
    'hgta_track': 'knownGene',
    'hgta_table': 'knownGene',
    'hgta_regionType': 'genome',
    'position': 'chr9:21802635-21865969',
    'hgta_outputType': 'primaryTable',
    'boolshad.sendToGalaxy': '0',
    'boolshad.sendToGreat': '0',
    'boolshad.sendToGenomeSpace': '0',
    'hgta_outFileName': '',
    'hgta_compressType': 'none',
    'hgta_doTopSubmit': 'get output'
}

params = {
    'hgsid':'605984071_MCAGID7KmBvssx6IJozA1Ou1XsSi',
    'jsh_pageVertPos': '0',
    'clade': 'mammal',
    'org': 'Mouse',
    'db': 'mm10',
    'hgta_group': 'genes',
    'hgta_track': 'knownGene',
    'hgta_table': 'kgAlias',
    'hgta_regionType': 'genome',
    'position': 'chr9:21802635-21865969',
    'hgta_outputType': 'primaryTable',
    'boolshad.sendToGalaxy': '0',
    'boolshad.sendToGreat': '0',
    'boolshad.sendToGenomeSpace': '0',
    'hgta_outFileName': '',
    'hgta_compressType': 'none',
    'hgta_doTopSubmit': 'get output'
}


def get_transcript_data():
    print ("Downloading {} table...".format(params2['hgta_table']))
    response = session.post(url, data=params2)
    raw_data = str(response.content)
    return raw_data


def get_transcript_aliases():
    print ("Downloading {} table...".format(params['hgta_table']))
    response = session.post(url,data = params)
    raw_data = str(response.content)
    return raw_data


def data_splitter(raw_data):
    lines = raw_data.split('\\n')
    # remove first and last elements, as they are not needed
    del lines[0]
    del lines[-1]
    lines = list(map(lambda x: x + '\n',lines))
    return lines


def write_to_file(data,path):
    print ("Writing {}...".format(path))
    with open(path, 'w') as f:
        f.writelines(data)


def main():
    transcript_data = data_splitter(get_transcript_data())
    transcript_aliases = data_splitter(get_transcript_aliases())
    write_to_file(transcript_aliases,'db/transcript_aliases.txt')
    write_to_file(transcript_data,'db/transcript_data.txt')

if __name__ == '__main__':
    main()

