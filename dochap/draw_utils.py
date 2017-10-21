import os
import svgwrite


class NormalizedDwg(svgwrite.Drawing):
    """
    An svg drawing with normalization values
    """
    a_length = 1
    nor_length = 400

def create_drawing(size = ('100%','100%'),a_len=1):
    """
     create a NormalizedDwg
     input:
     size: size in %, must be a string.
     output:
     dwg: svg drawing
    """

    dwg = NormalizedDwg(size=size)
    dwg.a_length = a_len
    return dwg

def add_style(dwg,style):
    """
     add a style for a drawing.
     input:
     dwg: svg drawing
     style: string of css style
     output:
     dwg: svg drawing
    """
    dwg.defs.add(dwg.style(style))
    return dwg

def add_line(dwg,position,size):
    """
     add a line to a drawing
     input:
     dwg: svg drawing
     position: start position tuple(x,y)
     size: tuple(x,y)
     output:
     line: reference to the line created.
    """
    # normalize size
    size = (size[0]/dwg.a_length)*dwg.nor_length,size[1]
    end = position[0]+size[0],position[1]+size[1]
    line = dwg.add(dwg.line(start=position,end=end,stroke=svgwrite.rgb(10, 10, 16, '%')))
    return line


def add_text(dwg,text, position,font_size = 20):
    """
    Add a text to the dwg

    Input:
        dwg - NormalizedDwg
        text - string
        position - Tuple(x,y)
        font_size - Int, font size of the text - defaults to 20
    """
    text = dwg.add((dwg.text(text=text,insert=normalize(dwg,position),font_size=font_size)))
    return text

def normalize(dwg,size):
    """
    Normalize the given size according to the values in dwg.

    Input:
        dwg - NormalizedDwg
        size - tuple(x,y)
    """
    size=(size[0]/dwg.a_length)*dwg.nor_length,size[1]
    return size

def add_rect(dwg, position, size,color='blue',tooltip=""):
    """
     add a rect to a drawing
     input:
         dwg: svg drawing
         position: start position -tuple (x,y)
         size: size of the rect tuple (width, height )
         color: color string/rgb for the rect. default to blue.
     output:
         rect: reference to the rect created.
    """


    rect = dwg.add(dwg.rect(insert=normalize(dwg,position),size = normalize(dwg,size),fill=color))
    rect.set_desc(tooltip)
    return rect

def main():
    pass

if __name__ == '__main__':
    main()

