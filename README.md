# Pleiades
Pleiades is a CLI tool to download and sort Objekts. \
Objekts are a digital photocard system used by the Kpop agency Modhaus.

## What does this do?

This repository provides a simple python script allowing to :
- Download objekts using the same API as [Pulsar](https://pulsar.azagal.eu) (an API I own and maintain).
- Sort objekts into folders, based on season then member.

Additionally a bash shell script allows to :
- Select all downloaded objekts from a date onward
- Compress them into a zip file for easier sharing

## Requirements

For the downloader
- Python 3.10+
- `python-dotenv` module
- `requests` module

For the shell script
- Any system with bash (Linux, WSL, etc...)

## Installation

```bash
git clone https://github.com/Azagal258/Pleiades.git
cd Pleiades/
pip install -r requirements.txt
cp .env.example .env
```
## How to use

Python script (downloader)\
`python3 quick_DL.py`

Shell script (packager) [works only on systems with a bash shell] :
```bash
chmod +x makezip.sh
./makezip.sh
```

## Configuration

.env contains by default :
- `save_path` : base directory where Objekts will be downloaded.

After the first complete run, it'll include automatically :
- `artms`, `triples` and `idntt` : the latest run timestamps for each group.

You can edit `save_path` so it points where you want your archive to reside.
The timestamps are used to prevent duplicates and ensure no Objekts are missed. I'd recommend to not edit them manually

## License
Copyright © 2024-2025 Azagal258

This project is licensed under the Mozilla Public License 2.0 (MPL 2.0).  
See the [LICENSE](./LICENSE.md) file for details.