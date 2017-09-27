import os
import sqlite3
import getopt
import sys
import conf

def parseGTF(filename):
    with open(filename) as f:
        content = f.readlines()
    userTranscripts = []
    transcript = []
    transcriptIDprev = ''
    geneIDprev = ''
    relativeStop = 0
    cds = []
    '''
    The relative start and stop values are relative to the finished protein.
    Here there are 2 cases. 1: if the read transcript is the same as the previous one so it need to be added to the
     same entry and the relative start and stop area need to be adjusted acording to the previous exon.
     2: the transcript is different than the previous one so everything must start again.
    '''
    for line in content:
        stline = line.split("\t")
        if stline[2] == 'exon':
            geneID = stline[8].split("\"")[1]
            transcriptID = stline[8].split("\"")[3]
            cdsStart = stline[3]
            cdsStop = stline[4]
            cdsLength = int(cdsStop) - int(cdsStart)
            # could do abs(cdsLength) +1
            if cdsLength > 0:
                cdsLength = cdsLength +1
            else:
                cdsLength = (-1)*cdsLength +1

            # same transcript
            if transcriptIDprev == transcriptID:
                relativeStart = relativeStop +1
                relativeStop = relativeStart + cdsLength
                exon = []
                # cds start,end,length, and where is it on the transcript
                exon.extend((cdsStart, cdsStop, cdsLength, relativeStart, relativeStop))
                cds.append(exon)
            else:
                relativeStart = 1
                relativeStop = relativeStart + cdsLength
                transcript.extend((geneIDprev, transcriptIDprev, cds))
                userTranscripts.append(transcript)
                cds = []
                exon = []
                transcript = []
                exon.extend((cdsStart, cdsStop, cdsLength, relativeStart, relativeStop))
                cds.append(exon)
            transcriptIDprev = transcriptID
            geneIDprev = geneID
    #print(userTranscripts)
    userTranscripts.pop(0)
    transcript.extend((geneIDprev, transcriptIDprev, cds))
    userTranscripts.append(transcript)
    return userTranscripts

help_message = "parser.py -i <inputfile> -o <outputfile> -s specie"

def main(argv):
    input_file = ''
    out_putfile =''
    specie = ''
    try:
        opts,args = getopt.getopt(argv,'h:i:o:s')
    except getopt.GetoptError:
        print(help_message)
        sys.exit(2)
    for opt,arg in opts:
        if opt == '-h':
            print(help_message)
            sys.exit()
        elif opt in ('-i','-ifile'):
           input_file = arg
        elif opt in('-o','-ofile'):
            output_file = arg
        elif opt in ('-s','-specie'):
            specie = arg
    if input_file =='' or specie = '':
        print(help_message)
        sys.exit()
    data = loadData('db/comb.db')
    for d in data[:5]:
        print (str(d) +'\n')
    #parsed_gtf =  parseGTF(input_file)
    #print (parsed_gtf[:10])
    #for transcript in parsed_gtf[:10]:
    #    print (assignDomainsToUExon(transcript))

def assignDomainsToExons(data):
    for transcript in data:
        relativeStart = 1
        relativeStop = 0
        for exon in transcript[4]:
            if exon[0] != '' and exon[1] != '':
                exonLength = int(exon[1])-int(exon[0])
                relativeStop = relativeStart + exonLength
                domainList = []
                for domain in transcript[3]:
                    if domain[1].isdigit():
                        domainNum = domain[0]
                        domainStart = int(domain[1])*3 -2
                        domainStop = int(domain[2])*3
                        if (relativeStart <= domainStart and domainStart <= relativeStop) or\
                              (relativeStart <= domainStop and domainStop <= relativeStop):
                            domainList.append(domainNum)
                exon.append(domainList)
                relativeStart = relativeStop + 1

# for a given transcript from gtf file, assign domains to exons
# call for every transcript of user
def assignDomainsToUExon(data,uTranscript):
    uTranscriptName = uTranscript[1]
    newUTranscript = []
    for transcript in data:
        transcriptName = transcript[2]
        if uTranscriptName == transcriptName:
            uExons = uTranscript[2]
            exons = transcript[4]
            for uExon in uExons:
                uExonStart = uExon[0]
                uExonStop = uExon[1]
                for exon in exons:
                    if len(exon) == 3:
                        exonStart = exon[0]
                        exonStop = exon[1]
                        exonDomains = exon[2]
                        if uExonStart <= exonStart and exonStop <= uExonStop:
                            uExon.append(exonDomains)
            newUTranscript.extend((uTranscript[0], uTranscript[1], transcript[3], uTranscript[2]))
            break
    return newUTranscript


def loadData(db_path,specie):
    with sqlite3.connect(conf.databases[specie]) as con:
        data =[]
        con.row_factory = sqlite3.Row
        cursor = con.cursor()
        result = cursor.execute("SELECT * FROM genebank ")
        while True:
            row = result.fetchone()
            if not row:
                    break
            # get the symbol
            symbol = row['symbol']
            coded_by= row['coded_by'].split(':')[0]
            # missing USCS transcript id
            transcript_id = ''
            sites = []
            regions = []
            sites_text = row['sites'].split(',')
            for s in sites_text:
                if s == '':
                    continue
                site = {}
                splitted = s.split('[')
                site['name'] = splitted[0]
                site['start'] = splitted[1].split(':')[0]
                site['end'] =splitted[1].split(':')[1].split(']')[0]
                sites.append(site)
            regions_text = row['regions'].split(',')
            for r in regions_text:
                if s == '':
                    continue
                region = {}
                splitted = s.split('[')
                region['name'] = splitted[0]
                region['start'] = splitted[1].split(':')[0]
                region['end'] =splitted[1].split(':')[1].split(']')[0]
                regions.append(region)
            # cds start and ends are missing (big numbers)
            # they are the exons start and end
            cds_numbers = []
            data.append((symbol,coded_by,transcript_id,sites,regions, cds_numbers))
        return data

if __name__ == '__main__':
    main(sys.argv[1:])
