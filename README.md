# dri-edm-tools
Scripts for working with an OAI-PMH EDM feed used to aggregate content to the Europeana platform. Includes a tool to export individual xml files (one per object) from the OAI-PMH EDM feed. This can be zipped and used as an alternative submission method, and can also be used with tools such as the Metis Sandbox https://metis-sandbox.eanadev.org/metis-sandbox-rest-production/swagger-ui.html#/dataset-controller

This was developed for use with the Digital Repository of Ireland's aggregation service, but there is no reason that it should not work for other aggregators.

# Installation
Install Python 3 for your system.

To use the Graphical User Interface install the Python 3 Tkinter module.

Clone the repository from Github.

# Running
## export.py
To export an EDM OAI-PMH feed to xml files run the export.py file by double clicking, or running from the command line.

Optional command-line parameters are --endpoint and --outputdir

If you do not pass the endpoint and outputdir on the command line you will be prompted to enter or select them. If you have Tkinter installed you can select these via a Graphical User Interface, otherwise they can be typed in on the command line.

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

