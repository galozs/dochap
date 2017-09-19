import os
import json
import visualizer
import progressbar
import domains_to_exons
import uuid

domains_db = 'db/domains.db'
# parse json file into dictionary
def parse_output_file(filename):
    with open(filename,'r') as f:
        json_dump = f.read()
        data = parse_output(json_dump)
    return data

# parse json string into dictionary
def parse_output(json_dump):
    transcripts_data = {}
    transcripts_data = json.loads(json_dump)
    return transcripts_data

def load_db_data(user_data):
    print ("loading db exons...")
    bar = progressbar.AnimatedProgressBar(end=len(user_data),width=10)
    bar +=1
    bar.show_progress()
    for key,item in user_data.items():
        #doms = domains_to_exons.get_domains(key)
        exons = domains_to_exons.get_exons_by_transcript_id(key)
        item.append(exons)
        bar+=1
        bar.show_progress()
    print("\ndone")


def load_and_visualize(output_file):
    data = parse_output_file(output_file)
    load_db_data(data)
    target_folder = str(uuid.uuid4())
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


def main():
    data = load_and_visualize('output.json')

if __name__ == '__main__':
    main()

