import sys
'''
DOCHAP (DOmain CHAnge Predictor) takes the data file containing the domain information made in Matlab and a gtf file from an
experiment. The domain Data file name will go in the loadData function and the user experiment file name will go in the
parseGTF function.
As an output you will get a file containing a list of the user's transcripts. For each transcript there will be a list
of domains that it probably contains and it's list of exons. It also contains a list of missing domains which are
the keys of domains that are in the transcript but aren't in any of the exons.
Each domain in a transcript contains a key and each exon contains a list of domain keys it probably contains.
The columns in the output file are delimited by ";" and the columns are:
GeneID;TranscriptID;Exons;MissingDomains

The exons are delimited by '|' and the data of each exon is delimitted by '@'
The data within each exon is as follows:
start location@stop location@list of domains in the exons

The data within each domain is delimited the same way:
domain key@domain start@domain stop@domain name
the list of domains in an exon is a list of the keys of each domain in the exon and they are delimited by '%'

The missing domains are delimited by '|'

Transcripts from the user data that aren't in the database or are predicted to not contain any domains are
left out.
'''

'''
Before running the program make sure you have the 2 input files in the same folder.
You can change these file names here as well as the output file name
'''
userGTFFileName = "transcripts.gtf"
dataFileName = "mrna_peptide.txt"

outputFileName = "transcriptsWdomains.txt"

delimiter1 = ";"
delimiter2 = "|"
delimiter3 = "@"
delimiter4 = "%"

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



def loadData(datafile):
    with open(datafile) as f:
        content = f.readlines()
        content.pop(0)
        data = []
    for line in content:
        stline = line.split(";")
        domainsT = stline[6].split("|")
        domains = []
        num = 1
        for doms in domainsT:
            stline2 = doms.split("@")
            stline2.insert(0, num)
            domains.append(stline2)
            num += 1
        domainsT = stline[7].split("|")
        for doms in domainsT:
            stline2 = doms.split("@")
            stline2.insert(0, num)
            domains.append(stline2)
            num += 1
        exons = []
        eStart = stline[17].split("|")
        eStop = stline[18].split("|")
        eStart.pop()
        eStop.pop()
        for (starts, stops) in zip(eStart, eStop):
            stline2 = []
            stline2.extend((starts, stops))
            exons.append(stline2)

        dataLine = []
        if domains[0][1] != '' or domains[1][1] != '':
            dataLine.extend((stline[3], stline[1], stline[19][:-2], domains, exons))
            data.append(dataLine)
    print(data[:5])
    return data

# needs to be done once for every upgrade of db
# after one use should add to db the new data
def assignDomainsToExons():
    # built from
    # 0.symbol
    # 1.np_1131311
    # 2.id
    # 3.[domains]
    # 4.[exon loc pairs]
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
                        # if domain start inside relative
                        # or if domain end inside relative
                        # add domain number to domainList of the exon
                        if (relativeStart <= domainStart and domainStart <= relativeStop) or\
                              (relativeStart <= domainStop and domainStop <= relativeStop):
                            domainList.append(domainNum)
                # add the domain list to the exon data
                exon.append(domainList)
                relativeStart = relativeStop + 1

def assignDomainsToUExon(uTranscript):
    uTranscriptName = uTranscript[1]
    newUTranscript = []
    for transcript in data:
        transcriptName = transcript[2]
        # if the transcript have the same id
        # terrible way of finding matches
        # should be done in sql query for the transcript id
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
                        # if the exon from user transcript contains all of the exon from the db
                        if uExonStart <= exonStart and exonStop <= uExonStop:
                            # tell the user exon that is contains the domains of the db exon
                            uExon.append(exonDomains)
            # add a new tuple of the user transcript data with new exonDomains information
            # to a new list
            newUTranscript.extend((uTranscript[0], uTranscript[1], transcript[3], uTranscript[2]))
            break
    return newUTranscript

def makeOutputFile(fileName):
    with open(fileName, "w") as f:
        for uTranscript in userTranscripts:
            # get user exons data for every transcript
            newUTranscript = assignDomainsToUExon(uTranscript)
            if newUTranscript != []:
                uTranscript = newUTranscript
                finalLine = uTranscript[0] + delimiter1 + uTranscript[1] + delimiter1
                domainsLine = ""
                domainsList = []
                for domain in uTranscript[2]:
                    if domain[1].isdigit():
                        domainsLine = domainsLine + str(domain[0]) + delimiter3 + str(domain[1]) + delimiter3 +\
                                      str(domain[2]) + delimiter3 + domain[3] + delimiter2
                        domainNum = []
                        domainNum.extend((domain[0], 0))
                        domainsList.append(domainNum)
                domainsLine = domainsLine[:-1]
                finalLine = finalLine + domainsLine + delimiter1
                exonsLine = ""
                for exon in uTranscript[3]:
                    exonsLine = exonsLine + str(exon[0]) + delimiter3 + str(exon[1])
                    if len(exon) == 6:
                        exonDomains = ""
                        for domain in exon[5]:
                            exonDomains = exonDomains + str(domain) + delimiter4
                            for edomain in domainsList:
                                if edomain[0] == domain:
                                    edomain[1] += 1
                        exonDomains = exonDomains[:-1]
                    exonsLine = exonsLine + delimiter3 + exonDomains + delimiter2
                exonsLine = exonsLine[:-1]
                missingDomains = ""
                for edomain in domainsList:
                    if edomain[1] == 0:
                        missingDomains = missingDomains + str(edomain[0]) +delimiter2

                missingDomains = missingDomains[:-1]
                finalLine = finalLine + exonsLine + delimiter1 + missingDomains
                f.write(finalLine + "\n")
            else:
                uTranscript.append("Transcript not in Database")

data = loadData(dataFileName)
userTranscripts = parseGTF(userGTFFileName)
assignDomainsToExons()
makeOutputFile(outputFileName)

