# dri-edm-tools
Scripts for working with an OAI-PMH EDM feed. Includes a tool to export individual xml files (one per object) from the OAI-PMH EDM feed. This can be zipped and used as an alternative submission method, and can also be used with tools such as the Metis Sandbox https://metis-sandbox.eanadev.org/metis-sandbox-rest-production/swagger-ui.html#/dataset-controller

This was developed for use with the Digital Repository of Ireland's aggregation service, but there is no reason that it should not work for other aggregators.

# Installation
Install Python 3 for your system.

To use the Graphical User Interface install the Python 3 Tkinter module.

Clone the repository from Github.

# Running
To export an EDM OAI-PMH feed to xml files run the export.py file by double clicking, or running from the command line.

Optional command-line parameters are --endpoint and --outputdir

If you do not pass the endpoint and outputdir on the command line you will be prompted to enter or select them. If you have Tkinter installed you can select these via a Graphical User Interface, otherwise they can be typed in on the command line.

