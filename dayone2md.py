import re
import json
from pathlib import Path
import yaml
import maya
import click
import copy
from typing import *


class DayOneJsonReader:
    def __init__(self, jsonpath: Path) -> None:
        self.jsonpath = jsonpath
        self.jsonobj = None

    def read(self):
        with self.jsonpath.open('r') as f:
            self.jsonobj = json.load(f)

        # Simple validation
        assert tuple(self.jsonobj.keys()) == ('metadata', 'entries')
        assert self.jsonobj.get('metadata').get('version') == '1.0'
        return self

    def __call__(self) -> Dict[str, Union[Dict, List, Any]]:
        if self.jsonobj is not None:
            return self.jsonobj
        else:
            raise AttributeError('Read json file first.')

    @property
    def entries(self):
        return self.jsonobj['entries']


class EntryConverter:
    def __init__(self, entry: Dict[str, Any]) -> None:
        self.metadata = entry
        self.text = self.metadata.pop('text')
        self.converted: Union[str, None] = None
        self.creation_date = self._creation_date()
        assert self.metadata.get('text') is None

    def _creation_date(self) -> str:
        """Format creationDate string using maya, to make datetime string macos friendly"""
        return maya.parse(self.metadata.get('creationDate')).iso8601().replace(':', '')

    def _format_metadata(self) -> str:
        metadata_string = yaml.dump(self.metadata, allow_unicode=True, default_flow_style=False)
        return metadata_string

    def to_markdown(self, **kwargs) -> Tuple[str, str]:
        s = f"---\n{self._format_metadata()}\n---\n\n\n{self.text}\n"
        self.converted = s
        return (self.creation_date, self.converted)


class MdWriter:
    def __init__(self, fn: Path, entry: Dict[str, Union[Dict, List, Any]]) -> None:
        self.fn = fn
        self.entry = entry

    def write(self, force=False) -> None:
        _fn = self.fn.with_suffix('.md')
        if _fn.exists() and not force is True:
            raise FileExistsError(f'File {_fn} exists')
        else:
            with _fn.open('w') as f:
                f.write(self.entry)


def _prepare_destination(dest: Path) -> None:
    dest.mkdir(exist_ok=True, parents=True)
    (dest / Path('photos')).mkdir(exist_ok=True)


@click.command()
@click.argument('jsonpath')
@click.argument('destination')
@click.option('--overwrite', is_flag=True, help='Force overwrite when exporting entries')
def dayone2md(jsonpath, destination, overwrite):
    """Convert *.json exported by DayOne2.app to Pandoc Markdown"""
    reader = DayOneJsonReader(Path(jsonpath))
    entries = reader.read().entries

    if entries is not None:
        dest = Path(destination)
        _prepare_destination(dest)

    converted: List[Tuple[str, str]] = []
    for e in entries:
        converted.append(EntryConverter(entry=e).to_markdown())

    for _t in converted:
        ts, s = _t
        filename = dest / Path(ts)
        try:
            MdWriter(fn=filename, entry=s).write(force=overwrite)
        except (FileExistsError) as e:
            print(e)


def main():
    dayone2md()


if __name__ == '__main__':
    main()
