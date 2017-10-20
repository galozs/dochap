import os
import svgwrite
from svgwrite import cm,mm,rgb
from draw_utils import create_drawing, add_style, add_line, add_rect, normalized_dwg


LINE_HEIGHT = 40

# input:
# transcripts: dictionary of tuples of user data and db data
def visualize(transcripts):
    index= 0
    for transcript_id,data in transcripts.items():
        index+=1
        if index ==20:
            break
        if not data:
            continue
        list_of_variants, exons_in_database = data
        print('visualize {}'.format(transcript_id))
        create_svgs(transcript_id, list_of_variants, exons_in_database)


# create the svgs
def create_svgs(transcript_id,user_variants,db_exons_variants):
    user_graphs = draw_user_graphs(user_variants)
    db_graphs = draw_db_graphs(db_exons_variants)
    set_links(user_graphs, db_graphs)

def draw_user_graphs(user_variants):
    for index, variant in enumerate(user_variants):
        print('variant is:', variant)
        if 'u_exons' not in variant:
            continue

        exons = variant['u_exons']
        domains = variant['domains']
        dwg = NormalizedDwg()
        name = variant['name']
        dwg.filename = 'testing/variant_{}_{}.svg'.format(name,index)
        start = (exons[0]['relative_start'] + 40, LINE_HEIGHT)
        end = (exons[-1]['relative_end'] + 40,LINE_HEIGHT)
        dwg.a_length = end[0]-start[0]
        add_line(dwg,start,end)
        for exon in variant['u_exons']:
            position= exon['relative_start']+40,LINE_HEIGHT*2
            length = exon['relative_end'] - exon['relative_start']
            size = length,LINE_HEIGHT
            add_rect(dwg,position,size)
        dwg.save()
    # for every variant:
    # draw line with numbers
    # draw domains under the line
    # draw exons under the domains
    pass

def draw_db_graphs(db_exons_variants):
    # for every variant:
    # draw line with numbers
    # draw domains under the line
    # draw exons under the domains
    pass

def set_links(user_graphs,db_graphs):
    pass


def main():
    pass

if __name__ == '__main__':
    main()

