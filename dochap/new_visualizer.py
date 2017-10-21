import os
import svgwrite
from svgwrite import cm,mm,rgb
from draw_utils import create_drawing, add_style, add_line, add_rect 


LINE_HEIGHT = 40
style = '''
        text
        { visibility: hidden;   pointer-events: none;}
        #shown
        { visibility: visible; }
        rect:hover
        { opacity: 0.5; }
        rect:hover ~ text
        { visibility: visible; }
        '''
def visualize(transcripts):
    """
     input:
     transcripts: dictionary of tuples of user data and db data
    """
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


def create_svgs(transcript_id,user_variants,db_exons_variants):
    """
     create the svgs
    """
    user_graphs = draw_user_graphs(user_variants)
    db_graphs = draw_db_graphs(db_exons_variants)
    set_links(user_graphs, db_graphs)

def draw_user_graphs(user_variants):
    """
    """
    for index, variant in enumerate(user_variants):
        print('variant is:', variant)
        if 'u_exons' not in variant:
            continue

        exons = variant['u_exons']
        domains = variant['domains']
        dwg = create_drawing()
        add_style(dwg,style)
        name = variant['name']
        dwg.filename = 'testing/variant_{}_{}.svg'.format(name,index)
        start = (exons[0]['relative_start'] , LINE_HEIGHT)
        size = (exons[-1]['relative_end'] ,0)
        dwg.a_length = size[0]
        add_line(dwg,start,size)
        for exon in variant['u_exons']:
            position= exon['relative_start'],LINE_HEIGHT*2
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
    """
    """
    # for every variant:
    # draw line with numbers
    # draw domains under the line
    # draw exons under the domains
    pass

def set_links(user_graphs,db_graphs):
    """
    """
    pass


def main():
    pass

if __name__ == '__main__':
    main()

