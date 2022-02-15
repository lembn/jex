import os
import hashlib
from typing import Callable
from datetime import datetime
import click

conv: Callable[[str], str] = lambda x: x.replace("\\", "/")
join: Callable[[str, str], str] = lambda x, y: conv(os.path.join(x, y))
format_classpath: Callable[[str], str] = lambda x: f"{x}/*"

silent = False


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


def time() -> str:
    return datetime.now().strftime("%H:%M:%S")


def log(message: str, type: str = "INFO", colour: str = "white") -> None:
    if silent:
        return
    message = f"{type} [{time()}]: {message}"
    click.echo(
        click.style(
            message,
            bold=True,
            fg=colour,
        )
    )


def set_silent():
    global silent
    silent = True
