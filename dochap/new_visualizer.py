import os
import svgwrite
from svgwrite import cm,mm,rgb
from draw_utils import create_drawing, add_style, add_line, add_rect,add_text
import pathlib


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
def visualize(transcripts,specie):
    """
     input:
     transcripts: dictionary - keys are transcripts id, values are dictionaries with keys exons,domains
    """
    for transcript_id,transcript_data in transcripts.items():
        if not transcipt_data:
            print('no transcript data for ',transcript_id)
            continue
        user_exons = transcript_data['exons']
        db_domains = transcript_data['domains']
        db_exons = get_db_data(transcript_id,specie)

        create_svgs(transcript_id,user_exons,db_exons,db_domains)

def get_db_data(transcript_id,specie):
    """
    get the exons data from the database,
    of all the transcripts asocciated with the given transcript id aliases.

    input:
        transcript_id - string
        specie: string of the specie (must be one from conf.py)
    """
    pass

def create_svgs(transcript_id,user_variants,db_exons_variants):
    """
     create the svgs
    """
    user_graphs = draw_user_graphs(user_variants,db_exons_variants)
    db_graphs = draw_db_graphs(db_exons_variants)
    set_links(user_graphs, db_graphs)

def draw_user_graphs(user_variants,db_exons_variants):
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
        if not db_exons_variants:
            print('no db_exons_variants')
            break
        prefix = 'testing/variant_{}'.format(name)
        # create the path
        pathlib.Path(prefix).mkdir(parents=True,exist_ok=True)
        dwg.filename = prefix+'/{}_{}.svg'.format(name,index)
        start = (exons[0]['relative_start'] , LINE_HEIGHT)
        size = (exons[-1]['relative_end'] ,0)
        dwg.a_length = size[0]
        add_line(dwg,start,size,True)
        for exon in variant['u_exons']:
            position= exon['relative_start'],LINE_HEIGHT*3
            length = exon['relative_end'] - exon['relative_start']
            size = length,LINE_HEIGHT
            add_rect(dwg,position,size,tooltip=str(exon))
        add_text(dwg,'exons',(dwg.a_length,position[1]+LINE_HEIGHT/2))
        for domain in domains:
            start = int(domain['start']) * 3 - 2
            end = int(domain['end']) * 3
            position = start,LINE_HEIGHT*2
            length = end-start
            size = length,LINE_HEIGHT
            add_rect(dwg,position,size,'green',str(domain))
        add_text(dwg,'domains',(dwg.a_length,position[1]+LINE_HEIGHT/2))
        dwgs.append(dwg)
        dwg.save()
    if dwgs != []:
        return dwgs
    # draw exons without domains from db
    dwg = create_drawing()
    try:
        prefix = 'testing/'+user_variants[0]['transcript_id']+'/'
        dwg.filename = prefix+user_variants[0]['transcript_id']+'.svg'
    except:
        user_variants = [user_variants]
        prefix = 'testing/'+user_variants[0]['transcript_id']+'/'
        dwg.filename = prefix+user_variants[0]['transcript_id']+'.svg'
    pathlib.Path(prefix).mkdir(parents=True,exist_ok=True)
    dwg.a_length = int(user_variants[-1]['relative_end'])
    start = (1,LINE_HEIGHT)
    size = (dwg.a_length,0)
    add_line(dwg,start,size,True)
    for exon in user_variants:
        start = int(exon['relative_start'])
        end = int(exon['relative_end'])
        position = start,LINE_HEIGHT*3
        size = end-start,LINE_HEIGHT
        add_rect(dwg,position,size,tooltip=str(exon))
    print('saving',dwg.filename)
    dwg.save()

def draw_db_graphs(db_exons_variants):
    """
    """
    if db_exons_variants:
        prefix = 'testing/variant_'+db_exons_variants[0]['alias']+'/db_'
    if not db_exons_variants:
        print('no db_exons_variants')
        return
    for variant_index,variant in enumerate(db_exons_variants):
        for trans_id,variant_dict in variant['exons_variants_data'].items():
            for gene_name,exons in variant_dict.items():
                dwg = create_drawing()
                dwg.filename = prefix + '{}_{}.svg'.format(variant['alias'],variant_index)
                position = exons[0]['exon_rel_start'],LINE_HEIGHT
                size = exons[-1]['exon_rel_end'],0
                dwg.a_length = size[0]
                add_line(dwg,position,size,True)
                domains = extract_domains(exons)
                print('domains are: ',domains)
                input()
                for domain in domains:
                    start = int(domain['start']) * 3 - 2
                    end = int(domain['end']) * 3
                    position = start,LINE_HEIGHT*2
                    size = end-start,LINE_HEIGHT
                    add_rect(dwg,position,size,tooltip=str(domain))

                for exon in exons:
                    start = exon['exon_rel_start']
                    end = exon['exon_rel_end']
                    position = start,LINE_HEIGHT * 3
                    size = end-start,LINE_HEIGHT
                    add_rect(dwg,position,size,tooltip=str(exon))
                print('saving db data:',dwg.filename)
                input()
                dwg.save()
    # for every variant:
    # draw line with numbers
    # draw domains under the line
    # draw exons under the domains



def extract_domains(exons):
    """
    extract a list of unique domains from a bunch of exons

    input:
        exons: list of exons (dictionaries)
    """
    domains = []
    for exon in exons:
        for domain in exon['domains_list']:
            domains.append(domain)
    # NEED TO JSON LOAD SHIT
    print(domains)
    print()
    domains = list(set(domains))
    print('doms are:',domains)
    input()
    return domains

def set_links(user_graphs,db_graphs):
    """
    """
    pass


def main():
    pass

if __name__ == '__main__':
    main()

