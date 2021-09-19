# Squiddy

PenTester's assistant.
Written poorly in python.

<img src="https://raw.githubusercontent.com/jayrox/squiddy/main/doc/main.png" height=25% width=25% />

# Install
uses [pysimplegui](https://pypi.org/project/PySimpleGUI/)

> pip install PySimpleGUI


# Generate CWE Templates
* cwe_parser powershell requires the xml file downloaded from https://cwe.mitre.org/data/downloads.html
* launch powershell
* cd to cwe_parser
* copy extracted cwe xml file into cwe_parser folder
* run parse.ps1
* copy the json files generated into the templates folder

# Run
> python gui.py

# Generate exe
> cd to squiddy's path

> pip install pyinstaller

> build.bat
