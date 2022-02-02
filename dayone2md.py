#!/usr/bin/env python3
import os
import re
import json
from pathlib import Path
import shutil
import sys
import yaml
import maya
import click
from typing import *


class DayOneJsonReader:
    def __init__(self, jsonpath: Path) -> None:
        self.jsonpath = jsonpath
        self.jsonobj = None

    def read(self):
        with self.jsonpath.open("r") as f:
            self.jsonobj = json.load(f)

        # Simple validation
        assert tuple(self.jsonobj.keys()) == ("metadata", "entries")
        assert self.jsonobj.get("metadata").get("version") == "1.0"
        return self

    def __call__(self) -> Dict[str, Union[Dict, List, Any]]:
        if self.jsonobj is not None:
            return self.jsonobj
        else:
            raise AttributeError("Read json file first.")

    @property
    def entries(self):
        return self.jsonobj["entries"]


class EntryConverter:
    def __init__(self, entry: Dict[str, Any]) -> None:
        self.metadata = entry
        self.text = self.metadata.pop("text")
        self.converted: Union[str, None] = None
        self.creation_date = self._creation_date()
        assert self.metadata.get("text") is None

    def _creation_date(self) -> str:
        """Format creationDate string using maya, to make datetime string macos friendly"""
        return maya.parse(self.metadata.get("creationDate")).iso8601().replace(":", "")

    def _format_metadata(self) -> str:
        metadata_string = yaml.dump(
            self.metadata, allow_unicode=True, default_flow_style=False
        )
        return metadata_string

    def _replace_image_urls(self):
        image_metadata = self.metadata.get("photos")
        if image_metadata:
            id_to_md5 = {d.get("identifier"): d.get("md5") for d in image_metadata}
            id_to_fileext = {d.get("identifier"): d.get("type") for d in image_metadata}
            for img_id, md5 in id_to_md5.items():
                imageurl = re.compile(f"dayone-moment:\/\/{img_id}")
                if imageurl.search(self.converted) is not None:
                    self.converted = imageurl.sub(
                        f'photos/{md5}.{id_to_fileext.get(img_id, "jpeg")}',  # TODO: Better file ext fallback
                        self.converted,
                    )

    def to_markdown(self, **kwargs) -> Tuple[str, str]:
        if self.text.startswith("#"):
            prefix = ""
        else:
            prefix = "# "
        body = prefix + self.text
        self.converted = f"---\n{self._format_metadata()}\n---\n\n\n{body}\n"
        self._replace_image_urls()
        return (self.creation_date, self.converted)


class MdWriter:
    def __init__(self, dest_dir: Path) -> None:
        self.dest_dir = dest_dir

    def write(self, timestamp: str, content: str, force=False) -> None:
        _fn = self.dest_dir / Path(timestamp).with_suffix(".md")
        if _fn.exists() and not force is True:
            raise FileExistsError(f"File {_fn} exists")
        else:
            with _fn.open("w") as f:
                f.write(content)
        # set accessed-time and modified time
        epoch = maya.parse(timestamp).epoch
        os.utime(_fn, (epoch, epoch))


def _prepare_destination(src: Path, dest: Path) -> None:
    dest.mkdir(exist_ok=True, parents=True)
    try:
        shutil.copytree(str(src / Path("photos")), str(dest / Path("photos")))
    except FileExistsError as e:
        print('"photos" directory exists, skipped copying.', file=sys.stderr)


@click.command()
@click.argument("jsonpath")
@click.argument("destination")
@click.option(
    "--overwrite", is_flag=True, help="Force overwrite when exporting entries"
)
def dayone2md(jsonpath, destination, overwrite):
    """Convert *.json exported by DayOne2.app to Pandoc Markdown"""
    reader = DayOneJsonReader(Path(jsonpath))
    entries = reader.read().entries

    if entries is not None:
        src = Path(jsonpath).parent
        dest = Path(destination)
        _prepare_destination(src, dest)

    converted: List[Tuple[str, str]] = []
    for e in entries:
        try:
            converted.append(EntryConverter(entry=e).to_markdown())
        except KeyError as ke:
            print(
                f"Entry of {e.get('creationDate')} seems to have no body text.",
                file=sys.stderr,
            )

    for _t in converted:
        ts, s = _t
        mdwriter = MdWriter(dest_dir=dest)
        try:
            mdwriter.write(ts, s, force=overwrite)
        except (FileExistsError) as e:
            print(e, end="", file=sys.stderr)
            print(
                ". Use '--overwrite' option if you want to overwrite.", file=sys.stderr
            )


def main():
    dayone2md()


if __name__ == "__main__":
    main()
