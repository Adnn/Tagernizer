#!/usr/bin/env python3

import os
import glob
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm, inch

from PIL import Image

import argparse, math

""" Tagernizer is a collection of helpers to organize rectangulars tags (images) on whites labels paper
 and generate a PDF.
Important remarks : the API uses ReportLab coordinate system, with origin at the BOTTOM-left, positive x axis going to the right of the page, and positive y axis going up.
The length unit of the coordiante system is the 'point', which is 1/72th of an inch."""

# It seems standard in publication to use the 'point' mesure unit (1/72 of an inch). It's the case for ReportLab.
# Coordinates are expressed at an equivalent 72 dpi resolution
# Nb : printers' resolution are way bigger, so it is perfectly sane to use fractions of this unit.
STANDARD_72 = 72.
#printer resolution in dpi
RESOLUTION = 1200
#define a 1 (printer) dot thickness in the 'point' unit.
LINE_WIDTH = STANDARD_72*1./RESOLUTION

# Printers can show some offset when printing page (you can mesure it printing the result of draw_outline)
# A positive offset means the printed dot is further away on the positive axis from the theoritical dot.
PRINTERS = {
    # No offset
    "ideal": (0., 0.),
    # hp psc2355
    "hp-psc2355": (0.6*mm, -1.*mm),
}

# standard A4
PAGE_WIDTH = 210.*mm
PAGE_HEIGHT = 297.*mm

# DECAdry DLW1736 (48 labels/page) paper layout, in mm :
# margins : top 20.6 bottom 22 left/right : 10
LABEL_MARGIN_TOP=20.7*mm
LABEL_MARGIN_BOTTOM=21.9*mm
LABEL_MARGIN_LEFT=9.9*mm
LABEL_MARGIN_RIGHT=10.1*mm

LABEL_WIDTH = 45.7*mm
LABEL_HEIGHT = 21.2*mm
LABEL_HMARGIN = 2.4*mm
LABEL_VMARGIN = 0.

LABEL_HPERIOD = LABEL_WIDTH + LABEL_HMARGIN
LABEL_VPERIOD = LABEL_HEIGHT + LABEL_VMARGIN

LABEL_HCOUNT = 4
LABEL_VCOUNT = 12


class Rectangle(object):
    """ dumb struct """
    def __init__(self, topleft, topright, bottomright, bottomleft):
        self.topleft=topleft
        self.topright=topright
        self.bottomright=bottomright
        self.bottomleft=bottomleft


def get_printable_corners(offset):
    return Rectangle(
        (LABEL_MARGIN_LEFT - offset[0],             PAGE_HEIGHT-LABEL_MARGIN_TOP - offset[1]),
        (PAGE_WIDTH-LABEL_MARGIN_RIGHT - offset[0], PAGE_HEIGHT-LABEL_MARGIN_TOP - offset[1]),
        (PAGE_WIDTH-LABEL_MARGIN_RIGHT - offset[0], LABEL_MARGIN_BOTTOM - offset[1]),
        (LABEL_MARGIN_LEFT - offset[0],             LABEL_MARGIN_BOTTOM - offset[1]),
    )


def draw_outline(canvas, printzone):
    canvas.saveState()
    canvas.setLineWidth(LINE_WIDTH)

    canvas.line(*(printzone.topleft     + printzone.topright))
    canvas.line(*(printzone.topright    + printzone.bottomright))
    canvas.line(*(printzone.bottomright + printzone.bottomleft))
    canvas.line(*(printzone.bottomleft  + printzone.topleft))

    canvas.restoreState()


def draw_cells(canvas, printzone):
    def component_addition(collec_a, collec_b):
        return [a+b for a, b in zip(collec_a, collec_b)]

    canvas.saveState()
    canvas.setLineWidth(LINE_WIDTH)
    canvas.setDash(4, 4)

    for row in range(1, LABEL_VCOUNT):
        canvas.line(
            *(component_addition(printzone.bottomleft, (0., row*LABEL_VPERIOD))
            +
            component_addition(printzone.bottomright, (0., row*LABEL_VPERIOD))) )

        if LABEL_VMARGIN:
            canvas.line(
                *(component_addition(printzone.bottomleft, (0., row*LABEL_VPERIOD-LABEL_VMARGIN))
                +
                component_addition(printzone.bottomright, (0., row*LABEL_VPERIOD-LABEL_VMARGIN))) )



    for col in range(1, LABEL_HCOUNT):
        canvas.line(
            *(component_addition(printzone.topleft, (col*LABEL_HPERIOD, 0.))
            +
            component_addition(printzone.bottomleft, (col*LABEL_HPERIOD, 0.))) )

        if LABEL_HMARGIN:
            canvas.line(
                *(component_addition(printzone.topleft, (col*LABEL_HPERIOD-LABEL_HMARGIN, 0.))
                +
                component_addition(printzone.bottomleft, (col*LABEL_HPERIOD-LABEL_HMARGIN, 0.))) )

    canvas.restoreState()


def insert_image(canvas, printzone, image_file, col, row):
    image = Image.open(image_file)
    # Image dimension in mm at printer's DPI
    width, height = [(float(dim))/RESOLUTION*inch for dim in image.size]

    if width>LABEL_WIDTH or height>LABEL_HEIGHT:
        raise Exception('Image "'+image_file+'" is bigger than paper\'s label at current resolution ('+str(RESOLUTION)+').')

    if row>=LABEL_VCOUNT or col>=LABEL_HCOUNT:
        raise Exception('Label position ('+str(row)+', '+str(col)+') is outside the paper.')

    v_padding = LABEL_HEIGHT - height
    h_padding = LABEL_WIDTH - width

    lower_left_corner = (
            printzone.topleft[0] + col*LABEL_HPERIOD + h_padding/2,
            printzone.topleft[1] - (row*LABEL_VPERIOD + v_padding/2 + height))

    canvas.drawImage(image_file, *lower_left_corner, width=width, height=height)


def generate_labels_page(args, extension, output_canvas=None, output_filename="labels.pdf"):
    if output_canvas==None:
        output_canvas = canvas.Canvas(os.path.join(args.directory, output_filename))

    printzone = get_printable_corners(PRINTERS[args.printer])
    first_available_label=(args.col, args.row)

    files = [file for file in glob.glob(os.path.join(args.directory, '*.'+extension)) for i in range(args.repeat)]
    first_label_id = first_available_label[1]*LABEL_HCOUNT  + first_available_label[0]
    for label_id, label_file in zip([x+first_label_id for x in range(len(files))], files):
        insert_image(output_canvas, printzone, label_file, label_id%LABEL_HCOUNT, math.floor(label_id/LABEL_HCOUNT))

    if args.print_guides:
        draw_outline(output_canvas, printzone)
        draw_cells(output_canvas, printzone)

    output_canvas.save()
    return output_canvas


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate a ready to print PDF file presenting all tags from a given folder.')
    parser.add_argument('directory', help='The directory containing all tags to be processed')
    parser.add_argument('printer', choices=["ideal", "hp-psc2355"], help='A printer from the list of hardcoded presets')
    parser.add_argument('--col', type=int, default = 0, help='column of the first free label (zero based index)')
    parser.add_argument('--row', type=int, default = 0, help='row of the first free label (zero based index)')
    parser.add_argument('--repeat', type=int, default = 2, help='cardinality for each label')
    parser.add_argument('--print-guides', action="store_true",
                        help='print a solid rectangle around the printzone, and dashes between cells')
    args = parser.parse_args()

    generate_labels_page(args, 'png')
