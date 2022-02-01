#!/usr/bin/env python

import argparse
import os
import tempfile
from urllib import request, parse
from lxml import etree as ET

gui = True
try:
    from tkinter import simpledialog
    from tkinter import filedialog
    from tkinter import *
except ImportError:
    gui = False

global img

def main():
    endpoint, outputdir = setup()
    with tempfile.TemporaryDirectory() as tmpdir:
        get_edm(endpoint, tmpdir)
        split_files(tmpdir, outputdir)


## Get the OAI endpoint and outputdir by hook or by crook!
## If the machine has Tkinter installed we can use a graphical
## file browser. Otherwise the user can enter the params on the
## command line or via an input prompt
## The multiple methods are there to make it as easy as possible
## for users with different needs and experience to use the tool
def setup():
    parser = argparse.ArgumentParser()
    parser.add_argument('--endpoint', help='The OAI endpoint')
    parser.add_argument('--outputdir', help='The output directory')
    args = parser.parse_args()

    if gui:
        app = Tk()
        app.title("DRI EDM Export")
        canvas = Canvas(app, width = 100, height = 100)
        canvas.pack()      
        img = PhotoImage(file="./assets/dri_ident_tiny.png")      
        canvas.create_image(20,20, anchor=NW, image=img)      
        endpoint = args.endpoint or simpledialog.askstring("endpoint",
                                    "Enter the OAI endpoint",
                                    parent=app)
        outputdir = args.outputdir or filedialog.askdirectory(initialdir = ".",
                                    title = "Select output diretory")
    else:
        endpoint = args.endpoint or input("Please enter the OAI endpoint  ")
        outputdir = args.outputdir or input("Please enter the output directory ")

    endpoint = endpoint.rstrip()
    outputdir = outputdir.rstrip()

    if not parse.urlparse(endpoint).scheme in ('http', 'https'):
        print("Endpoint is not a valid URL")
        sys.exit(1)

    try:
        f = request.urlopen(endpoint)
    except ValueError:
        print("Endpoint is not reachable")
        sys.exit(1)

    return endpoint, outputdir


## gets the OAI-PMH feed from the endpoint and resumption token urls
## stores them in the temporary directory
def get_edm(endpoint, tmpdir):

    # Get the base OAI url for additional pages
    parsed_url = parse.urlparse(endpoint)
    filecount = 1;

    # Get all content from the OAI-PMH feed
    while endpoint:
        filename = os.path.join(tmpdir, str(filecount))
        request.urlretrieve(endpoint, filename)
        xml = ET.parse(filename)
        root = xml.getroot()
        try:
            token = root.findall(".//{http://www.openarchives.org/OAI/2.0/}resumptionToken")[0].text
        except IndexError:
            token = ""

        if token:
            endpoint = parse.urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, "", "verb=ListRecords&resumptionToken="+token , ""))
        else:
            endpoint = ""

        filecount = filecount+1


# processes the downloaded files
# parses out the records and saves each as a separate file in the output dir
def split_files(tmpdir, outputdir):
    dl = os.listdir(tmpdir)
    for f in dl:
        infile = os.path.join(tmpdir, f)
        xml = ET.parse(infile)
        root = xml.getroot()
        rdfs = root.findall(".//{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF")
        for entry in rdfs:
            filename = (entry[0].attrib['{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about']).replace("#","")
            outfile = os.path.join(outputdir, filename + ".xml")
            ET.ElementTree(entry).write(outfile, encoding='utf-8', xml_declaration=True)



if __name__ == '__main__':
    main()
