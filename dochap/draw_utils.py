import os
import svgwrite


class NormalizedDwg(svgwrite.Drawing):
    a_length = 1
    nor_length = 400

# create an svg drawing
# input:
# size: size in %, must be a string.
# output:
# dwg: svg drawing
def create_drawing(size = ('100%','100%')):
    dwg = NormalizedDwg(size=size)
    return dwg

# add a style for a drawing.
# input:
# dwg: svg drawing
# style: string of css style
# output:
# dwg: svg drawing
def add_style(dwg,style):
    dwg.defs.add(dwg.style(style))
    return dwg

# add a line to a drawing
# input:
# dwg: svg drawing
# start: start position tuple(x,y)
# end: end position tuple(x,y)
# output:
# line: reference to the line created.
def add_line(dwg,start,end):
    # normalize size
    end[0] = dwg.nor_length 
    line = dwg.add(dwg.line(start=start,end=end))
    return line

# add a rect to a drawing
# input:
# dwg: svg drawing
# position: start position -tuple (x,y)
# size: size of the rect tuple (width, height )
# output:
# rect: reference to the rect created.
def add_rect(dwg, position, size):
    rect = dwg.add(dwg.rect(insert=position,size=size))
    return rect

def main():
    pass

if __name__ == '__main__':
    main()

