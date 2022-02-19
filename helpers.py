from io import TextIOWrapper
import os
import hashlib
from typing import Callable
from datetime import datetime
import click


class ConfigLoadError(Exception):
    def __init__(self, message):
        super().__init__(message)


conv: Callable[[str], str] = lambda x: x.replace("\\", "/")
join: Callable[[str, str], str] = lambda x, y: conv(os.path.join(x, y))
updated: Callable[[str, str, str], bool] = (
    lambda name, hashes, file_hash, bin_path: name not in hashes
    or not hashes[name] == file_hash
    or not os.path.exists(bin_path)
)

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


def safe_conv(path: str) -> None:
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"The path '{path}' provided from configuration file does not exist."
        )
    else:
        return conv(path)


def validate_array(arr: list[str], name: str) -> None:
    if not isinstance(arr, list):
        raise ConfigLoadError(f"Invalid '{name}' - must be an array.")
    if arr == []:
        raise ConfigLoadError(f"If '{name}' is specified it cannot be empty.")


def prune(root: str, dirs: list[str]) -> None:
    for dir in dirs:
        dir = join(root, dir)
        if not os.listdir(dir):
            os.removedirs(dir)


def overwrite(file: TextIOWrapper, data: str) -> None:
    file.seek(0)
    file.truncate()
    file.write(data)
