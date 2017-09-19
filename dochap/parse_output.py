import os
import json
import visualizer
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


def main():
    data = parse_output_file('output.json')
    for index, (key,item) in enumerate(data.items()):
        if not 100 < index < 150:
            continue
        visualizer.visualize_transcript(item)

if __name__ == '__main__':
    main()

