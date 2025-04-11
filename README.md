# Py-Win-Deploy-Tools
WIP Tool suite for deploying embedded python applications in Windows

# Tools and Scripts

### add-dependencies.py: add extra dependencies to an embedded python package.
Usage:
1. Download get-pip.py from https://bootstrap.pypa.io/get-pip.py
2. Download an embeddable python package, such as https://www.python.org/ftp/python/3.13.1/python-3.13.1-embed-amd64.zip.
3. Run script to add your requirements from a `requirements.txt` file:
```
python .\add-dependencies.py .\get-pip.py .\python-3.13.3-embed-amd64.zip .\requirements.txt .\modified-python-3.13.3-embed-amd64.zip
```
