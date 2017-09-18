import os
import svgwrite
from svgwrite import cm,mm,rgb

def main():
    pass

TRANSCRIPT_HEIGHT=40

def visualize_transcript(transcript):
    exons = transcript[0]
    domains = transcript[1]
    draw_transcript(exons,domains)

def draw_transcript(exons,domains):
    if not exons:
        print('no exons')
        return
    #transcript_start = int(exons[0]['start'])
    #transcript_end = int(exons[-1]['end'])
    rel_start = 1
    rel_end = int(exons[-1]['relative_end'])
    gene_name = exons[0]['gene_id']
    transcript_id = exons[0]['transcript_id']
    # draw the transcript
    dwg = svgwrite.Drawing(filename=transcript_id+'.svg',size=('100%','100%'))
    draw_rect(dwg,(0,0),rel_end - rel_start,TRANSCRIPT_HEIGHT)
    draw_domains(dwg,domains)
    draw_exons(dwg,exons)
    dwg.save()

def draw_rect(dwg,position,width,height,line_color='red',fill_color='None'):
    dwg.add(dwg.rect(id="myrect",insert=position,size=(width,height),fill=line_color,stroke='black'))
    t = dwg.add(dwg.text(text="someamzaing tooltip",id="thepopup",insert=(10,10),font_size=20,fill="black",visibility="hidden"))
    animator = t.add(svgwrite.animate.Animate())
    animator.set_timing(begin="myrect.mouseover",end="myrect.mouseout")
    animator.set_target("visibility")
    animator.set_value(values=['visibility'],from_="hidden",to="visible")
    dwg.add(dwg.line(start=(0,height-10),end=(0,height+10),stroke='black',stroke_width=2))
    dwg.add(dwg.line(start=(width,height-10),end=(width,height+10),stroke='black',stroke_width=2))



def add_comment(g,comment):
    pass

def draw_domains(dwg,domains):
    domains_g = dwg.add(dwg.g(id='domains',font_size=14))
    if not domains:
        domains_g.add(dwg.text("no domains",(0,50)))
        return
    for domain in domains:
        draw_domain(domain)

def draw_exons(dwg,exons):
    exons_g = dwg.add(dwg.g(id='exons',font_size=14))
    if not exons:
        exons_g.add(dwg.text("no exons",(0,100)))
        return
    for exon in exons:
        draw_exon(exon)

def draw_domain(domain):
    pass

def draw_exon(exon):
    pass



if __name__ == '__main__':
    main()

