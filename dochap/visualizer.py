import os
import svgwrite
from svgwrite import cm,mm,rgb
import pathlib
running_height = 0
max_width = 0

def main():
    pass

def set_width(value):
    global max_width
    max_width = value

RECT_HEIGHT=40
SPACING = 20
# input:
# folder: path to the folder inside svgs folder
# transcript: iterable with user_exons,domains,db_exons
def visualize_transcript(folder,transcript):
    pathlib.Path('svgs/{}'.format(folder)).mkdir(parents=True, exist_ok=True)

    user_exons = transcript[0]
    domains = transcript[1]
    db_exons = transcript[2]
    draw_transcript(folder,user_exons,domains,db_exons)

def draw_transcript(folder,user_exons,domains, db_exons):
    running_height = 0
    if not user_exons:
        print('no user exons')
        return
    #transcript_start = int(user_exons[0]['start'])
    #transcript_end = int(user_exons[-1]['end'])
    rel_start = 1
    rel_end = int(user_exons[-1]['relative_end'])
    set_width(rel_end)
    gene_name = user_exons[0]['gene_id']
    transcript_id = user_exons[0]['transcript_id']
    # draw the transcript
    dwg = svgwrite.Drawing(filename='svgs/{}/{}.svg'.format(folder,transcript_id),size=('100%','100%'))
    dwg.defs.add(dwg.style('''
        text
        { visibility: hidden;   pointer-events: none;}
        #shown
        { visibility: visible; }
        rect:hover
        { opacity: 0.5; }
        rect:hover ~ text
        { visibility: visible; }
        '''))
    draw_rect(dwg,(1,0),rel_end-1,RECT_HEIGHT,text=transcript_id, is_trans=True)
    #dwg.add(dwg.text(text=str(rel_start),insert=(rel_start,RECT_HEIGHT+1+running_height),font_size=20))
    #dwg.add(dwg.text(text=str(rel_end),insert=(rel_end,RECT_HEIGHT+1+running_height),font_size=20))
    running_height += RECT_HEIGHT + SPACING
    draw_domains(dwg,domains,running_height)
    draw_user_exons(dwg,user_exons,running_height)
    draw_db_exons(dwg,db_exons,running_height)
    dwg.save()



def normalize(value):
    if max_width == 0:
        print("failed to normalize")
        return value
    return value/max_width * 400

def draw_rect(dwg,position,width,height,fill_color='red',stroke_color='black',text=None,is_trans=False,tooltip_text = None):
    start_txt = str(position[0])
    end_txt = str(position[0] + width)
    width = normalize(width)
    position = normalize(position[0]),position[1]
    g = dwg.add(dwg.g(opacity=0.8))

    rect = g.add(dwg.rect(id="myrect",insert=position,size=(width,height),fill=fill_color,stroke=stroke_color))
    if tooltip_text:
        rect.set_desc(title=tooltip_text,desc=tooltip_text)
    if text:
        text_pos = position[0] + width/2,position[1] + height/3
        g.add(dwg.text(text=text,id="shown",insert=text_pos,font_size=20,style="text-anchor: middle; dominant-baseline: hanging;"))

    dwg.add(dwg.line(start=(position[0],position[1]+height-10),end=(position[0],position[1]+height+10),stroke='black',stroke_width=2))
    dwg.add(dwg.line(start=(position[0]+width,position[1]+height-10),end=(position[0]+width,position[1]+height+10),stroke='black',stroke_width=2))

    g.add(dwg.text(text=start_txt,insert=(position[0],position[1]+RECT_HEIGHT+running_height),font_size=14))
    mod = 0
    if is_trans:
        mod = RECT_HEIGHT
    g.add(dwg.text(text=end_txt,insert=(position[0]+width,position[1]+running_height+mod),font_size=14))
    return g
    #print (start_txt,' ',end_txt)

def draw_domains(dwg,domains,running_height):
    if not domains:
        dwg.add(dwg.text("no domains",(0,50)))
        return
    #print(dwg.filename)
    for domain in domains:
        draw_domain(dwg,domain)
    running_height += SPACING*3

def draw_domain(dwg,domain):
    start = int(domain['start'])*3 - 2
    end = int(domain['end']) * 3
    domain['start'] = start
    domain['end'] = end
    position = (start,running_height+2*SPACING)
    height = RECT_HEIGHT/2
    width = end-start
    g = draw_rect(dwg,position,width,height,'blue','black',tooltip_text=str(domain))
    #domain_data_pos = (0, position[1]+running_height+SPACING*4)
    #g.add(dwg.text(text=str(domain),insert=domain_data_pos,font_size=14))

def draw_user_exons(dwg,exons,running_height):
    exons_g = dwg.add(dwg.g(id='exons',font_size=14))
    if not exons:
        exons_g.add(dwg.text("no exons",(0,100)))
        return
    for exon in exons:
        draw_exon(dwg,exon,running_height)
    running_height += SPACING*3

def draw_db_exons(dwg,exons,running_height):
    exons_g = dwg.add(dwg.g(id='db_exons',font_size=14))
    if not exons:
        exons_g.add(dwg.text("no db_exons",(0,100)))
        return
    for exon in exons:
        draw_exon(dwg,exon,running_height+SPACING,color='yellow')
    running_height += SPACING*3



def draw_exon(dwg,exon,running_height,color=None):
    if not color:
        color = 'green'
    start = int(exon['relative_start'])
    end = int(exon['relative_end'])
    width = end-start
    position = start,running_height
    height = RECT_HEIGHT/2
    g = draw_rect(dwg,position ,width,height,color,'black',tooltip_text=str(exon))
    #exon_data_pos = (0, position[1]+SPACING*4)
    #g.add(dwg.text(text=str(exon),insert=exon_data_pos,font_size=14))



if __name__ == '__main__':
    main()

