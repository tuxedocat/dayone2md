dayone2md
==========

This is a simple exporter script for `DayOne.app (Version 2)`.  

Each entry in `journal_name.json` will be exported as *Pandoc Markdown* with DayOne's metadata.  
The script also copies attached photos in `photos` directory to the output directory.


Requirements
-------------

* Python 3.7 or higher.
    * You may need Homebrew, Anaconda, or pyenv to use the latest version of python.
* Python packages
    * [poetry](https://github.com/python-poetry/poetry) for managing dependencies. 
    * See `pyproject.toml` for other dependencies.

> I tested this script with Python 3.9, and is tested on WSL2 env.

Install
--------

If you don't have `poetry` and Python 3.x, setup them using homebrew by `brew install python3 poetry` or by other tools.

Just copy `dayone2md.py` to somewhere, or clone this repository.

```sh
$ git clone https://github.com/tuxedocat/dayone2md.git
$ cd dayone2md
$ poetry install
```

Usage
---------

Your journal file should be exported by DayOne.app as 'JSON in Zip' and extracted into certain directory, for example:

```sh
<some_dir>
    -- journal_name.json        JSON file exported from DayOne.app
    -- photos/                  Directory containing photos 
```

Then run this script from your terminal. 

```sh
# You may need run this script as
# poetry run python dayone2md.py 

# Show help (long-form only)
$ python dayone2md.py --help
    Usage: dayone2md.py [OPTIONS] JSONPATH DESTINATION

    Convert *.json exported by DayOne2.app to Pandoc Markdown

    Options:
    --overwrite  Force overwrite when exporting entries
    --help       Show this message and exit.

# Like this. output_dir will be created automatically.
$ python dayone2md.py export_dir/Journal.json output_dir

# Note that entries already existing in the destination directory will not be overwritten.
$ ls output_dir
    2017-07-15T153143Z.md  2017-07-31T150815Z.md  2018-02-16T143957Z.md  2018-02-19T110856Z.md  photos/

# In such case, use --overwrite option.
$ python dayone2md.py --overwrite export_dir/Journal.json output_dir
```
