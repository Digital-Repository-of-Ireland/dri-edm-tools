#!/usr/bin/env python

import argparse
import os
import tempfile
from lxml import etree as ET
from urllib.parse import urlparse
import requests
import re
import sparql
import geocoder
from datetime import datetime

gui = True
try:
    from tkinter import simpledialog
    from tkinter import filedialog
    from tkinter import *
except ImportError:
    gui = False

nsmap = {"xml": "http://www.w3.org/XML/1998/namespace"}

global img

def main():
    inputdir, outputdir, geonameskey = setup()
    with tempfile.TemporaryDirectory() as tmpdir:
        convert(inputdir, outputdir, geonameskey)


## Get the inputdir and outputdir by hook or by crook!
## If the machine has Tkinter installed we can use a graphical
## file browser. Otherwise the user can enter the params on the
## command line or via an input prompt
## The multiple methods are there to make it as easy as possible
## for users with different needs and experience to use the tool
def setup():
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputdir', help='The input directory')
    parser.add_argument('--outputdir', help='The output directory')
    parser.add_argument('--geonameskey', help='Geonames.org key (username), sign up on geonames.org and enable Free web services')
    args = parser.parse_args()

    if gui:
        app = Tk()
        app.title("DRI map EDM Contextual Classes")
        canvas = Canvas(app, width = 100, height = 100)
        canvas.pack()      
        img = PhotoImage(file="./assets/dri_ident_tiny.png")
        canvas.create_image(20,20, anchor=NW, image=img)
        inputdir = args.inputdir or filedialog.askdirectory(initialdir = ".",
                                    title = "Select input diretory")
        outputdir = args.outputdir or filedialog.askdirectory(initialdir = ".",
                                    title = "Select output diretory")
        geonameskey = args.geonameskey or simpledialog.askstring("geonameskey",
                                    "Geonames.org key (username), sign up on geonames.org and enable Free web services",
                                    parent=app) 
    else:
        inputdir = args.inputdir or input("Please enter the input directory ")
        outputdir = args.outputdir or input("Please enter the output directory ")
        geonameskey = args.geonameskey or input("Enter the Geonames.org key (username), sign up on geonames.org and enable Free web services ")

    inputdir = inputdir.rstrip()
    outputdir = outputdir.rstrip()

    return inputdir, outputdir, geonameskey


## parse each file in the inputdir, convert to dc and output to output dir
def convert(inputdir, outputdir, geonameskey):

    infiles = os.listdir(inputdir)
    for f in infiles:
        infile = os.path.join(inputdir, f)
        tree = ET.parse(infile)
        root = tree.getroot()

        #Create skos concepts for subject urls
        for subject in root.iter('{http://purl.org/dc/elements/1.1/}subject'):
            resource = subject.attrib.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource')

            if resource is not None:
                if ("getty" in resource):
                    q = ('SELECT ?label WHERE { '
                    '<'+resource+'> '
                    '<http://www.w3.org/2004/02/skos/core#prefLabel> ?label .}')
                    result = sparql.query('http://vocab.getty.edu/sparql', q)
                elif ("wikidata" in resource):
                    item = re.search('https?://www.wikidata.org/wiki/(Q.*)$', resource).group(1)
                    q = ('SELECT ?ll WHERE { wd:'+item+' rdfs:label ?ll }')
                    result = sparql.query('https://query.wikidata.org/sparql', q)
                else:
                    next

                skosconcept = ET.SubElement(root, "{http://www.w3.org/2004/02/skos/core#}concept", attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about':"#"+resource})

                for row in result:
                    value = row[0].value
                    lang = row[0].lang
                    preflabel = ET.SubElement(skosconcept, "{http://www.w3.org/2004/02/skos/core#}prefLabel", attrib={'{http://www.w3.org/XML/1998/namespace}lang':lang})
                    preflabel.text = value


        #Create edm places for spatial urls
        for place in root.iter('{http://purl.org/dc/terms/}spatial'):
            resource = place.attrib.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource')
            
            if resource is not None:
                if ("geonames" in resource):
                    item = re.search('https?://www.geonames.org/(.*)$', resource).group(1)
                    g = geocoder.geonames(item, method='details', key=geonameskey)
                    value = g.address
                    lang = "en"
                    coords = [g.lng, g.lat]
                    make_edmplace(root, resource, value, lang, coords)
                elif ("wikidata" in resource):
                    item = re.search('https?://www.wikidata.org/wiki/(Q.*)$', resource).group(1)
                    q = ('SELECT ?label ?location WHERE { wd:'+item+' rdfs:label ?label . '
                        ' wd:'+item+' wdt:P625 ?location '
                        'SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }')
                    result = sparql.query('https://query.wikidata.org/sparql', q)
                    for row in result:
                        if (row[0].lang == "en"):
                            value = row[0].value
                            lang = row[0].lang
                            point = row[1].value
                            coords = re.search('Point\((.*)\)',point).group(1).split()
                            make_edmplace(root, resource, value, lang, coords)

        ## resolve type to string
        for dctype in root.iter('{http://purl.org/dc/elements/1.1/}type'):
            r = dctype.attrib.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource')

            if r is not None:
                resource = r.replace("page/", "")
                if ("getty" in resource):
                    q = ('SELECT ?label WHERE { '
                    '<'+resource+'> '
                    '<http://www.w3.org/2004/02/skos/core#prefLabel> ?label .}')
                    result = sparql.query('http://vocab.getty.edu/sparql', q)
                elif ("wikidata" in resource):
                    item = re.search('https?://www.wikidata.org/wiki/(Q.*)$', resource).group(1)
                    q = ('SELECT ?ll WHERE { wd:'+item+' rdfs:label ?ll }')
                    result = sparql.query('https://query.wikidata.org/sparql', q)
                else:
                    next

                providedCHO = root[0]

                for row in result:
                    if (row[0].lang == "en"):
                        value = row[0].value
                        lang = row[0].lang
                        typeElement = ET.SubElement(providedCHO, "{http://purl.org/dc/elements/1.1/}type", attrib={'{http://www.w3.org/XML/1998/namespace}lang':lang})
                        typeElement.text = value

        ## crate timespan for temporal
        for place in root.iter('{http://purl.org/dc/terms/}temporal'):
            resource = place.attrib.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource')

            if resource is not None:
                if ("wikidata" in resource):
                    item = re.search('https?://www.wikidata.org/wiki/(Q.*)$', resource).group(1)
                    q = ('SELECT ?label ?start ?end WHERE { wd:'+item+' rdfs:label ?label . '
                        ' wd:'+item+' wdt:P580 ?start . '
                        ' wd:'+item+' wdt:P582 ?end '
                        'SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }')
                    result = sparql.query('https://query.wikidata.org/sparql', q)
                for row in result:
                    if (row[0].lang == "en"):
                        value = row[0].value
                        lang = row[0].lang
                        start = row[1].value
                        end = row[2].value
                        make_edmtimespan(root, resource, value, lang, start, end)

        # Output the new dc XML tree
        outfile = os.path.join(outputdir, f)
        tree.write(outfile, encoding='utf-8', xml_declaration=True)

## Functions

def make_edmplace(root, resource, value, lang, coords):
    edmplace = ET.SubElement(root, "{http://www.europeana.eu/schemas/edm/}place", attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about':"#"+resource})

    preflabel = ET.SubElement(edmplace, "{http://www.w3.org/2004/02/skos/core#}prefLabel", attrib={'{http://www.w3.org/XML/1998/namespace}lang':lang})
    preflabel.text = value
    longitude = ET.SubElement(edmplace, "{http://www.w3.org/2003/01/geo/wgs84_pos#}long")
    longitude.text = coords[0]
    latitude = ET.SubElement(edmplace, "{http://www.w3.org/2003/01/geo/wgs84_pos#}lat")
    latitude.text = coords[1]


def make_edmtimespan(root, resource, value, lang, start, end):
    edmtimespan = ET.SubElement(root, "{http://www.europeana.eu/schemas/edm/}TimeSpan", attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about':"#"+resource})

    preflabel = ET.SubElement(edmtimespan, "{http://www.w3.org/2004/02/skos/core#}prefLabel", attrib={'{http://www.w3.org/XML/1998/namespace}lang':lang})
    preflabel.text = value
    beginel = ET.SubElement(edmtimespan, "{http://www.europeana.eu/schemas/edm/}begin")
    beginel.text = datetime.strptime(start, '%Y-%m-%dT%H:%M:%SZ').strftime("%Y-%m-%d")
    endel = ET.SubElement(edmtimespan, "{http://www.europeana.eu/schemas/edm/}end")
    endel.text = datetime.strptime(end, '%Y-%m-%dT%H:%M:%SZ').strftime("%Y-%m-%d")

if __name__ == '__main__':
    main()
