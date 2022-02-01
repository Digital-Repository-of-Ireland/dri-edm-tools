# dri-edm-tools
This repo holds a number of scripts for working with Europeana EDM metadata. They were developed for use with the Digital Repository of Ireland's aggregation service, but they may prove useful for other aggregators.

The scripts are written in python and bash. We've tried to make them somewhat cross-platform, but they were mainly written and tested for Linux.

Includes:
- check.py - given an OAI-PMH EDM endpoint, checks that all of the records contain a metadata element and gives a report on missing elements.
- export.py - given an OIA-PMH EDM endpoint, downloads the OAI-PMH feed and splits out the EDM records into individual files
- add-isPartOf.sh - adds an isPartOf element with the project code, used for project reporting
- move-urls-to-resources.sh - takes linked-data URIs from the text of an element to an rdf:resource attribute of that element
- mapclasses.py - creates EDM Contextual classes when it finds relevant linked-data URIs in certain enabling element fields according to the Europeana Publishing Framework Metadata quality rules


# Installation
Install a Linux Bash shell for your system.

Install Python 3 for your system.

To use the Graphical User Interface install the Python 3 Tkinter module.

Clone the repository from Github.

# Running

## check.py
To check the EDM OAI-PMH feed run check.py from the command line (currently the report won't display via the GUI).

Command-line parameters are --endpoint. If you don't pass the endpoint you will be prompted for it.

The script will print a report identifying any records which have no metadata.

## export.py
To export an EDM OAI-PMH feed to xml files run the export.py file by double clicking, or running from the command line.

Optional command-line parameters are --endpoint and --outputdir

If you do not pass the endpoint and outputdir on the command line you will be prompted to enter or select them. If you have Tkinter installed you can select these via a Graphical User Interface, otherwise they can be typed in on the command line.

The output can be zipped and used as an alternative submission method, and can also be used with tools such as the Metis Sandbox https://metis-sandbox.eanadev.org/metis-sandbox-rest-production/swagger-ui.html#/dataset-controller

## add-isPartOf.sh
To add a dcterms:isPartOf field to identify records for a particular project use the add-isPartOf.sh script. 

Runs only from the command line on Unix systems or those with a bash shell installed.

```bash
./add-isPartOf.sh <Project code> <Directory containg the EDM files>
```

## move-urls-to-resources.sh
Sometimes linked data URIs appear as the text of an element, this script will move them to an rdf:resource attribute

Runs only from the command line on Unix systems or those with a bash shell installed.

```bash
./move-urls-to-resources.sh <directory>
```

## mapclasses.py
This script will perform SPARQL lookups on any URIs found as an rdf:resource attribute of the dc:subject, dcterms:spatial, dcterms:temporal and dc:type fields. It will create EDM contextual classes for subjects, places and timespans.

Optional command-line parameters are --endpoint and --outputdir and --geonameskey

If you do not pass these you will be prompted to enter or select them. If you have Tkinter installed you can select these via a Graphical User Interface, otherwise they can be typed in on the command line.

```bash
./mapclasses.py --inputdir=<Directory containing the EDM files> --outputdir=<output dir> --geonameskey=<key>
```

