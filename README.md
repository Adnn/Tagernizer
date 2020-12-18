# Tagernizer

Command line Python 3 helpers to organize rectangulars tags (images) on whites labels paper and generate a PDF.
This is intended as a companion to [Collecster](https://github.com/Adnn/Collecster), which generates tags for occurrences.

* **TagRenderPng**: render tags html to png images.
* **Tagernizer**: layout png images in a rectangular grid, outputting a PDF A4 page.

## Environment setup

    python3 -m venv venv
    source venv/bin/activate
    pip3 install -r requirements.txt
    deactivate

## Usage

Activate the virtual environment and see commands help:

    source venv/bin/activate
    ./TagRenderPng.p -h
    ./Tagernizer.p -h
