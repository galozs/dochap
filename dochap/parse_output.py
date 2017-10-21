import os
import json
import visualizer
import progressbar
import domains_to_exons
import uuid
import conf

domains_db = 'db/domains.db'

def parse_output_file(filename):
    """
     parse json file into dictionary
     input:
     filename: path to the output file of interface.py - must be json file.
     output:
     data: dictionary of the json data in the file.
    """
    with open(filename,'r') as f:
        json_dump = f.read()
        data = parse_output(json_dump)
    return data

def parse_output(json_dump):
    """
     parse json string into dictionary
     input:
     json_dump: string of json data 
     output:
     transcripts_data: the parsed json string data.
    """
    transcripts_data = {}
    transcripts_data = json.loads(json_dump)
    return transcripts_data

def load_db_data(user_data,specie):
    """
     load all the exons transcript data from the given transcripts names in the user_data
     input:
     user_data: dictionary created from the output file by parse_output_file
     specie: name of the specie from which to take the transcripts
    """
    print ("loading db exons...")
    bar = progressbar.AnimatedProgressBar(end=len(user_data),width=10)
    bar +=1
    bar.show_progress()
    for key,item in user_data.items():
        #doms = domains_to_exons.get_domains(key)
        exons = domains_to_exons.get_exons_by_transcript_id(key,specie)
        item.append(exons)
        bar+=1
        bar.show_progress()
    print("\ndone")

def load_and_visualize(data,specie):
    """
     parses the given output_file and create svgs from it.
     input:
     data: 
     output_file: path to the output file from interface.py
     specie: specie to visualize
     output:
     target_folder: path to the folder containing the new svgs
    """
    #data = parse_output_file(output_file)
    #load_db_data(data,specie)
    target_folder = str(specie) + '/' + str(uuid.uuid4())
    print("creating svgs...")
    bar = progressbar.AnimatedProgressBar(end=len(data),width=10)
    bar+=1
    bar.show_progress()
    for index, (key,item) in enumerate(data.items()):
        bar+=1
        bar.show_progress()
        visualizer.visualize_transcript(target_folder,item)
    print ('\ndone.')
    return target_folder


def main(output_file,specie):
    folder = load_and_visualize(output_file,specie)

if __name__ == '__main__':
    main('mouse_output', 'Mus_musculus')

