# Pleiades
Pleiades is a CLI tool to download and sort Objekts. \
Objetks are a digital photocard system used by the Kpop agency Modhaus.

## What does this do?

This repository provides a simple python script allowing to :
- Download objekts (with the API used by [Pulsar](https://pulsar.azagal.eu))
- Sort objekts into folders for ease of access

Additionally a bash shell script allows to :
- Select all objekts from a date onward
- Compress them into a zip file for ease of sharing

## Requirements

For the downloader
- Python 3.6+
- Python's `dotenv` module

For the shell script
- WSL or a system using bash

## Installation

```bash
python3 --version
git clone https://github.com/Azagal258/Pleiades.git
cd Pleiades/
pip install dotenv
```
## How to use

Python script (downloader)\
`python3 quick_DL.py`

Shell script (packager) [works only on systems with a bash shell] :
```bash
chmod +x makezip.sh
./makezip.sh
```

## License
Copyright © 2024-2025 Azagal258

This project is licensed under the Mozilla Public License 2.0 (MPL 2.0).  
See the [LICENSE](./LICENSE.md) file for details.
