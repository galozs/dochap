import os
import svgwrite
from svgwrite import cm,mm,rgb
from draw_utils import create_drawing, add_style, add_line, add_rect,add_text


LINE_HEIGHT = 40
style = '''
        text
        { visibility: visualize;   pointer-events: none;}
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
        if not data:
            continue
        try:
            list_of_variants, exons_in_database = data
        except:
            print('failed!')
            print('data: ',data)
            list_of_variants = data
            exons_in_database = None
            #continue
        #print('visualize {}'.format(transcript_id))
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
    dwgs = []
    for index, variant in enumerate(user_variants):
        if 'u_exons' not in variant:
            break
        exons = variant['u_exons']
        domains = variant['domains']
        dwg = create_drawing()
        add_style(dwg,style)
        name = variant['name']
        print('visualize',name)
        dwg.filename = 'testing/variant_{}_{}.svg'.format(name,index)
        start = (exons[0]['relative_start'] , LINE_HEIGHT)
        size = (exons[-1]['relative_end'] ,0)
        dwg.a_length = size[0]
        add_line(dwg,start,size)
        for exon in variant['u_exons']:
            position= exon['relative_start'],LINE_HEIGHT*3
            length = exon['relative_end'] - exon['relative_start']
            size = length,LINE_HEIGHT
            add_rect(dwg,position,size)
        add_text(dwg,'exons',(dwg.a_length,position[1]+LINE_HEIGHT/2))
        for domain in domains:
            start = int(domain['start']) * 3 - 2
            end = int(domain['end']) * 3
            position = start,LINE_HEIGHT*2
            length = end-start
            size = length,LINE_HEIGHT
            add_rect(dwg,position,size,'green','tooltip')
        add_text(dwg,'domains',(dwg.a_length,position[1]+LINE_HEIGHT/2))
        dwgs.append(dwg)
        dwg.save()
    if dwgs != []:
        return dwgs
    print('breaked')
    print('user_variants:',user_variants)
    # draw exons without domains from db
    dwg = create_drawing()
    try:
        dwg.filename = 'testing/'+user_variants[0]['transcript_id']+'.svg'
    except:
        user_variants = [user_variants]
        dwg.filename = 'testing/'+user_variants[0]['transcript_id']+'.svg'
        print('failed finding user_variants[0]:',user_variants)
    dwg.a_length = int(user_variants[-1]['relative_end'])
    start = (1,LINE_HEIGHT)
    size = (dwg.a_length,0)
    add_line(dwg,start,size)
    for exon in user_variants:
        start = int(exon['relative_start'])
        end = int(exon['relative_end'])
        position = start,LINE_HEIGHT*3
        size = end-start,LINE_HEIGHT
        add_rect(dwg,position,size)
    print('saving',dwg.filename)
    dwg.save()
        # draw exon
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

