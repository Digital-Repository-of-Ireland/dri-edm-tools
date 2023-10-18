#!/usr/bin/env python

import argparse
import os
import tempfile
from urllib import request, parse
from lxml import etree as ET
import sys
import time

gui = True
try:
    from tkinter import simpledialog
    from tkinter import *
except ImportError:
    gui = False

global img

def main():
    endpoint = setup()
    spinner = spinning_cursor()
    for _ in range(50):
        sys.stdout.write(next(spinner))
        sys.stdout.flush()
        time.sleep(0.1)
        sys.stdout.write('\b')
    with tempfile.TemporaryDirectory() as tmpdir:
        get_edm(endpoint, tmpdir)
        check_files(tmpdir)


## Get the OAI endpoint by hook or by crook!
## If the machine has Tkinter installed we can use a graphical
## file browser. Otherwise the user can enter the params on the
## command line or via an input prompt
## The multiple methods are there to make it as easy as possible
## for users with different needs and experience to use the tool
def setup():
    parser = argparse.ArgumentParser()
    parser.add_argument('--endpoint', help='The OAI endpoint')
    args = parser.parse_args()

    if gui:
        app = Tk()
        app.title("DRI EDM Check")
        canvas = Canvas(app, width = 100, height = 100)
        canvas.pack()      
        img = PhotoImage(file="./assets/dri_ident_tiny.png")      
        canvas.create_image(20,20, anchor=NW, image=img)      
        endpoint = args.endpoint or simpledialog.askstring("endpoint",
                                    "Enter the OAI endpoint",
                                    parent=app)
    else:
        endpoint = args.endpoint or input("Please enter the OAI endpoint  ")

    endpoint = endpoint.rstrip()

    if not parse.urlparse(endpoint).scheme in ('http', 'https'):
        print("Endpoint is not a valid URL")
        sys.exit(1)

    try:
        f = request.urlopen(endpoint)
    except ValueError:
        print("Endpoint is not reachable")
        sys.exit(1)

    return endpoint


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
def check_files(tmpdir):
    dl = os.listdir(tmpdir)
    validrecords = 0
    invalidrecords = [] 
    missinglang = []
    for f in dl:
        infile = os.path.join(tmpdir, f)
        xml = ET.parse(infile)
        root = xml.getroot()
        records = root.findall(".//{http://www.openarchives.org/OAI/2.0/}record")
        for entry in records:
            metadata = entry.find('{http://www.openarchives.org/OAI/2.0/}metadata')
            edmType = metadata.find('.//{http://www.europeana.eu/schemas/edm/}type')
            if (len(metadata) == 0):
                id = entry.find('{http://www.openarchives.org/OAI/2.0/}header').find('{http://www.openarchives.org/OAI/2.0/}identifier').text
                invalidrecords.append(id)
            elif edmType.text == "TEXT":
                id = entry.find('{http://www.openarchives.org/OAI/2.0/}header').find('{http://www.openarchives.org/OAI/2.0/}identifier').text
                lang = metadata.find('.//{http://purl.org/dc/elements/1.1/}language')
                if lang is None:
                    missinglang.append(id)
                    invalidrecords.append(id)
                else:
                    validrecords = validrecords+1
            else:
                validrecords = validrecords+1
                
    print_report(validrecords,invalidrecords, missinglang)


#Print out the results
#TODO: should be modified to work with GUI and maybe write the report to disk
def print_report(valid, invalid, missinglang):

    print("\n\n========= EDM Check ==================")
    print("Valid EDM records: "+str(valid))
    print("Invalid EDM records: "+str(len(invalid)))
    print("\n")

    if len(invalid) > 0:
        for id in invalid:
            print(id.replace("oai:dri:", "https://repository.dri.ie/catalog/"))

        print("Number of invalid TEXT records missing language: "+str(len(missinglang)))
        print("\n")

    for id in missinglang:
        print(id.replace("oai:dri:", "https://repository.dri.ie/catalog/"))


# Spinning Cursor
def spinning_cursor():
    while True:
        for cursor in '|/-\\':
            yield cursor


if __name__ == '__main__':
    main()
