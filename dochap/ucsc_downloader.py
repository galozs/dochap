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

humans_aliases = {
        'hgsid':'609792333_1QkTn4aGpxMwQjFdN9zh5F7zwJ1F',
        'jsh_pageVertPos':'0',
        'clade':'mammal',
        'org':'Human',
        'db':'hg38',
        'hgta_group':'genes',
        'hgta_track':'knownGene',
        'hgta_table':'kgAlias',
        'position':'chr1:3A11102837-11267747',
        'hgta_regionType':'genome',
        'hgta_outputType':'primaryTable',
        'boolshad.sendToGalaxy':'0',
        'boolshad.sendToGreat':'0',
        'boolshad.sendToGenomeSpace':'0',
        'hgta_outFileName':'',
        'hgta_compressType':'none',
        'hgta_doTopSubmit':'get output'
}
humans_gene_table = {
        'hgsid':'609792333_1QkTn4aGpxMwQjFdN9zh5F7zwJ1F',
        'jsh_pageVertPos':'0',
        'clade':'mammal',
        'org':'Human',
        'db':'hg38',
        'hgta_group':'genes',
        'hgta_track':'knownGene',
        'hgta_table':'knownGene',
        'position':'chr1:3A11102837-11267747',
        'hgta_regionType':'genome',
        'hgta_outputType':'primaryTable',
        'boolshad.sendToGalaxy':'0',
        'boolshad.sendToGreat':'0',
        'boolshad.sendToGenomeSpace':'0',
        'hgta_outFileName':'',
        'hgta_compressType':'none',
        'hgta_doTopSubmit':'get output'
}


def get_transcript_data():
    raw_data = []
    for param in [params2, humans_gene_table]:
        print ("Downloading {} table for {} genome...".format(param['hgta_table'],param['org']))
        response = session.post(url, data=param)
        raw_data.append((str(response.content),param))
    return raw_data


def get_transcript_aliases():
    raw_data = []
    for param in [params,humans_aliases ]:
        print ("Downloading {} table for {} genome...".format(param['hgta_table'],param['org']))
        response = session.post(url,data = params)
        raw_data.append((str(response.content),param))
    return raw_data


def data_splitter(raw_data):
    lines = raw_data.split('\\n')
    # remove first and last elements, as they are not needed
    del lines[0]
    del lines[-1]
    lines = list(map(lambda x: x + '\n',lines))
    return lines


def write_to_file(data,path):
    os.makedirs(os.path.dirname(path),exist_ok=True)
    print ("Writing {}...".format(path))
    with open(path, 'w') as f:
        f.writelines(data)


def main():
    transcript_data = get_transcript_data()
    transcript_aliases = get_transcript_aliases()
    for alias in transcript_aliases:
        name = 'db/'+alias[1]['org']+'/'+alias[1]['hgta_table']+'.txt'
        print ('alias name: ',name)
        write_to_file(data_splitter(alias[0]),name)
    for data in transcript_data:
        name = 'db/'+data[1]['org']+'/'+data[1]['hgta_table']+'.txt'
        print ('data name: ',name)
        write_to_file(data_splitter(data[0]),name)

if __name__ == '__main__':
    main()

