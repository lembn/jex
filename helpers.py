import os
import hashlib
from typing import Callable
from datetime import datetime
import click

conv: Callable[[str], str] = lambda x: x.replace("\\", "/")
join: Callable[[str, str], str] = lambda x, y: conv(os.path.join(x, y))


def hash_file(filename: str):
    BUF_SIZE = 65536  # 64Kb
    md5 = hashlib.md5()
    with open(filename, "rb") as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()


def log(message: str, type: str = "INFO", colour: str = "white") -> None:
    message = f"{type} [{datetime.now().strftime('%H:%M:%S')}]: {message}"
    click.echo(
        click.style(
            message,
            blink=True,
            bold=True,
            fg=colour,
        )
    )
