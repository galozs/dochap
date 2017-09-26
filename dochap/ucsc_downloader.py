import os
import ftplib
import requests
import progressbar
from sh import gunzip

# add species here to have correct placement in db folders
species = {
    'Mouse':'Mus_musculus'
    'Human':'Homo_sapiens'
}

url = "http://genome-euro.ucsc.edu/cgi-bin/hgTables"

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
# currently not in use
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
# currently not in use
humans_gene_table = {
        'hgsid':'609935507_iaCZKqxaqa997kPPi25VX3BSJHO2',
        'jsh_pageVertPos':'0',
        'clade':'mammal',
        'org':'Human',
        'db':'hg38',
        'hgta_group':'genes',
        'hgta_track':'knownGene',
        'hgta_table':'knownGene',
        'hgta_regionType':'genome',
        'position':'chr1%3A11102837-11267747',
        'hgta_outputType':'primaryTable',
        'boolshad.sendToGalaxy':'0',
        'boolshad.sendToGreat':'0',
        'boolshad.sendToGenomeSpace':'0',
        'hgta_outFileName':'test.txt',
        'hgta_compressType':'none',
        'hgta_doTopSubmit':'get output'
}
# ftp addresses for human data from ucsc
ftp_address = 'hgdownload.soe.ucsc.edu'
human_aliases = 'goldenPath/hg38/database/kgAlias.txt.gz'
human_knownGene = 'goldenPath/hg38/database/knownGene.txt.gz'


def get_transcript_data():
    raw_data = []
    for param in [params2]:
        session = requests.Session()
        print ("Downloading {} table for {} genome...".format(param['hgta_table'],param['org']))
        response = session.post(url, data=param)
        raw_data.append((str(response.content),param))
    return raw_data


def get_transcript_aliases():
    raw_data = []
    for param in [params]:
        session = requests.Session()
        print ("Downloading {} table for {} genome...".format(param['hgta_table'],param['org']))
        response = session.post(url,data = params)
        raw_data.append((str(response.content),param))
    return raw_data


def download_ftp_data(address,username,password,files):
    print('connecting to: ',address,'...')
    ftp = ftplib.FTP(address)
    print('logging in...')
    ftp.login(username,password)
    for file in files:
        os.makedirs(os.path.dirname(file[1]),exist_ok=True)
        print('downloading: ',file[0],'...')
        ftp.sendcmd("TYPE i")
        size = ftp.size(file[0])
        p_bar = progressbar.AnimatedProgressBar(end=size,width=10)
        with open(file[1]+'.gz','wb') as f:
            def callback(chunk):
                f.write(chunk)
                p_bar + len(chunk)
                p_bar.show_progress()
            ftp.retrbinary("RETR " + file[0], callback)
            p_bar + size
            p_bar.show_progress()
        print()
        print('extracting...')
        gunzip(file[1]+'.gz','-f')
        print('done')

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

def get_specie_name(specie):
    return species[specie]

def main():
    transcript_data = get_transcript_data()
    transcript_aliases = get_transcript_aliases()
    for alias in transcript_aliases:
        name = 'db/'+alias[1]['org']+'/'+alias[1]['hgta_table']+'.txt'
        print ('alias name: ',name)
        write_to_file(data_splitter(alias[0]),name)
    for data in transcript_data:
        name = 'db/'+get_specie_name(data[1]['org'])+'/'+data[1]['hgta_table']+'.txt'
        print ('data name: ',name)
        write_to_file(data_splitter(data[0]),name)

    ftp_files =[(human_aliases,'db/'+species['Human']+'/kgAliases.txt'),(human_knownGene,'db/Human/knownGene.txt')]
    download_ftp_data(ftp_address,'anonymous','elbazni@post.bgu.ac.il',ftp_files)

if __name__ == '__main__':
    main()

