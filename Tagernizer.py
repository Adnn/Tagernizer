from reportlab.pdfgen import canvas
from reportlab.lib.units import mm, inch

from PIL import Image

""" Tagernizer is a collection of helpers to organize rectangulars tags (images) on whites labels paper
 and generate a PDF.
Important remarks : the API uses ReportLab coordinate system, with origin at the BOTTOM-left, positive x axis going to the right of the page, and positive y axis going up.
The length unit of the coordiante system is the 'point', which is 1/72th of an inch."""

# It seems standard in publication to use the 'point' mesure unit (1/72 of an inch). It's the case for ReportLab.
#Coordinates are expressed at an equivalent 72 dpi resolution
#Nb : printers' resolution are way bigger, so it is perfectly sane to use fractions of this unit.
STANDARD_72 = 72.
#printer resolution in dpi
RESOLUTION = 1200
#define a 1 (printer) dot thickness in the 'point' unit.
LINE_WIDTH = STANDARD_72*1./RESOLUTION

#Printers can show some offset when printing page (you can mesure it printing the result of draw_outline)
#A positive offset means the printed dot is further away on the positive axis from the theoritical dot.
#hp psc2355
PRINTER_OFFSET = (0.*mm, -1.*mm)

#standard A4
PAGE_WIDTH = 210.*mm
PAGE_HEIGHT = 297.*mm

#DECAdry DLW1736 (48 labels/page) paper layout, in mm :
# margins : top 20.6 bottom 22 left/right : 10
M_TOP=20.6*mm + PRINTER_OFFSET[1]
M_BOTTOM=22.*mm - PRINTER_OFFSET[1]
M_LEFT=10.*mm -  PRINTER_OFFSET[0]
M_RIGHT=10.*mm + PRINTER_OFFSET[0]

LABEL_WIDTH = 45.7*mm
LABEL_HEIGHT = 21.2*mm
LABEL_HMARGIN = 2.4*mm
LABEL_VMARGIN = 0.

LABEL_HPERIOD = LABEL_WIDTH + LABEL_HMARGIN
LABEL_VPERIOD = LABEL_HEIGHT + LABEL_VMARGIN

LABEL_HCOUNT = 4
LABEL_VCOUNT = 12

#The corners of the print zone (top-left, top-right, bottom-righ, bottom-left)
A = (M_LEFT, PAGE_HEIGHT-M_TOP)
B = (PAGE_WIDTH-M_RIGHT, PAGE_HEIGHT-M_TOP)
C = (PAGE_WIDTH-M_RIGHT, M_BOTTOM)
D = (M_LEFT, M_BOTTOM)

def draw_outline(canvas):
    canvas.saveState()
    canvas.setLineWidth(LINE_WIDTH)

    canvas.line(*(A+B))
    canvas.line(*(B+C))
    canvas.line(*(C+D))
    canvas.line(*(D+A))

    canvas.restoreState()

def draw_cells(canvas):
    def component_addition(collec_a, collec_b):
        return [a+b for a, b in zip(collec_a, collec_b)]

    canvas.saveState()
    canvas.setLineWidth(LINE_WIDTH)
    canvas.setDash(4, 4)

    for row in range(1, LABEL_VCOUNT):
        canvas.line(
            *(component_addition(D, (0., row*LABEL_VPERIOD))
            +
            component_addition(C, (0., row*LABEL_VPERIOD))) )

        if LABEL_VMARGIN:
            canvas.line(
                *(component_addition(D, (0., row*LABEL_VPERIOD-LABEL_VMARGIN))
                +
                component_addition(C, (0., row*LABEL_VPERIOD-LABEL_VMARGIN))) )



    for col in range(1, LABEL_HCOUNT):
        canvas.line(
            *(component_addition(A, (col*LABEL_HPERIOD, 0.))
            +
            component_addition(D, (col*LABEL_HPERIOD, 0.))) )

        if LABEL_HMARGIN:
            canvas.line(
                *(component_addition(A, (col*LABEL_HPERIOD-LABEL_HMARGIN, 0.))
                +
                component_addition(D, (col*LABEL_HPERIOD-LABEL_HMARGIN, 0.))) )


    canvas.restoreState()

def insert_image(canvas, image_file, row, col):
    image = Image.open(image_file)
    width, height = [(float(dim))/RESOLUTION*inch for dim in image.size]

    if width>LABEL_WIDTH or height>LABEL_HEIGHT:
        raise Exception('Image "'+image_file+'" is bigger than paper\'s label at current resolution ('+str(RESOLUTION)+').')

    if row>=LABEL_VCOUNT or col>=LABEL_HCOUNT:
        raise Exception('Label position ('+str(row)+', '+str(col)+') is outside the paper.')

    v_padding = LABEL_HEIGHT - height
    h_padding = LABEL_WIDTH - width
    lower_left_corner = (
            M_LEFT + col*LABEL_HPERIOD + h_padding/2,
            PAGE_HEIGHT - (M_TOP + row*LABEL_VPERIOD + v_padding/2 + height))

    canvas.drawImage(image_file, *lower_left_corner, width=width, height=height)
