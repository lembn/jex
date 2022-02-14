import json
import platform
import re
import subprocess
import os
from typing import List
import click
import helpers
from config import Config

# TODO: add library support


def get_comp_list(config: Config) -> List[str]:
    if not os.path.exists(config.meta):
        os.makedirs(config.meta)
    if not os.path.exists(config.classes):
        with open(config.classes, "w") as hash_file:
            hash_file.write("{}")

    helpers.log("Collecting source files")
    with open(config.classes, "r+") as hash_file:
        hashes = json.load(hash_file)
        filenames = []

        compile = []
        for root, _, files in os.walk(config.sources):
            for name in files:
                if ".java" in name:
                    name = helpers.join(root, name)
                    filenames.append(name)
                    file_hash = helpers.hash_file(name)
                    bin_path = config.transform(name, True)
                    if (
                        name in hashes
                        and hashes[name] == file_hash
                        and os.path.exists(bin_path)
                    ):
                        continue
                    helpers.log(f"Found updated file: {name}")
                    compile.append(name)
                    hashes[name] = file_hash

        hashes = {i: j for i, j in hashes.items() if i in filenames}
        for root, dirs, files in os.walk(config.build):
            for name in files:
                if ".class" in name:
                    if "$" in name:
                        name = re.sub(r"\$.*", ".class", name)
                    name = helpers.join(root, name)
                    src_name = config.transform(name, False)
                    if src_name not in hashes:
                        os.remove(name)
            for dir in dirs:
                dir = helpers.join(root, dir)
                if not os.listdir(dir):
                    os.removedirs(dir)
        hash_file.seek(0)
        hash_file.truncate()
        hash_file.write(json.dumps(hashes))

        return compile


def execute(config: Config, compile: List[str], debug: bool, run: bool) -> None:
    opened = False
    bar = "===========================================\n"
    if compile:
        sep = ";" if platform.system() == "Windows" else ":"
        classpath = f"{config.build}{sep}{config.libs}" if config.libs else config.build
        helpers.log("Compiling...")
        result = subprocess.run(
            ["javac", "-classpath", classpath, "-d", config.build, *compile]
        )

        if result.stderr:
            run = False
            opened = True
            with open(config.errors, "a") as err_file:
                err_file.writelines([bar, helpers.time() + "\n", result.stderr])
            helpers.log(
                f"Occurred during compilation, check {os.path.abspath(config.errors)} for info.",
                type="ERROR",
                colour="red",
            )
            os.remove(config.classes)

    if run:
        program = "java"
        if debug:
            program = "jdb"
            helpers.log("DEBUG", colour="blue")
        helpers.log(f"Running from - {config.entry}")
        print()

        result = subprocess.run([program, "-classpath", config.build, config.entry])

        if result.stderr:
            with open(config.errors, "a") as err_file:
                if not opened:
                    err_file.writelines([bar, helpers.time() + "\n"])
                    opened = True
                err_file.write(result.stderr)
            helpers.log(
                f"Occurred during execution, check {os.path.abspath(config.errors)} for info.",
                type="ERROR",
                colour="red",
            )

    if opened:
        with open(config.errors, "a") as err_file:
            err_file.write(bar + "\n")


@click.command()
@click.version_option("1.3.4")
# The config options have no default so that their value will be None if they are
# not passed in the command line. This is done so that Config.adjust() will when
# it should or shouldn't overrdide file options
@click.option(
    "-c",
    "--config-path",
    default="./jex.json",
    show_default=True,
    type=click.Path(dir_okay=False),
    help="Path to the 'jex.json' configuration file.",
)
@click.option(
    "-b",
    "--build",
    type=click.Path(file_okay=False),
    help=f"Directory path to compile to. [default: {Config.BUILD_DEFAULT}]",
)
@click.option(
    "-s",
    "--sources",
    type=click.Path(exists=True, file_okay=False),
    help=f"Path to the containing directory of the source code. [default: {Config.SOURCES_DEFAULT}]",
)
@click.option(
    "-e",
    "--entry",
    type=click.STRING,
    help=f"Java FQN of the entry point file. [default: {Config.ENTRY_DEFAULT}]",
)
@click.option(
    "-l",
    "--libs",
    type=click.Path(exists=True, file_okay=False),
    help=f"Path to the containing directory of library files (*.jar). This option has no default, if not explicitly defined, no libaries will be passed to the compiler.",
)
@click.option(
    "-d",
    "--debug",
    default=False,
    show_default=True,
    type=click.BOOL,
    help="Run in debug mode.",
)
@click.option(
    "--compile/--no-compile",
    default=True,
    show_default=True,
    type=click.BOOL,
    help="Compile the project.",
)
@click.option(
    "--run/--no-run",
    default=True,
    show_default=True,
    type=click.BOOL,
    help="Run the entry point `main` method.",
)
@click.option(
    "-si",
    "--silent",
    is_flag=True,
    show_default=True,
    type=click.BOOL,
    help="Disable console logs.",
)
def main(
    config_path: str,
    build: str,
    sources: str,
    entry: str,
    libs: str,
    debug: bool,
    compile: bool,
    run: bool,
    silent: bool,
) -> None:
    """
    A lightweight wrapper for the Java CLI programs to act as a build tool
    for fast development of complex projects in a simple environment.

    \b
    jex.json format:
    {
        "build": ...,
        "sources": ...,
        "entry": ...,
        "lib": ...,
        "debug": ...
    }
    """

    if silent:
        helpers.set_silent()

    programs = [["java", "--version"], ["javac", "-version"]]
    if debug:
        programs.append(["jdb", "-version"])
    for program in programs:
        try:
            result = subprocess.run(
                program,
                capture_output=True,
                text=True,
            )
            version = re.sub("\n.*", "", result.stdout)
            helpers.log(version, type="", colour="green")
        except FileNotFoundError:
            helpers.log(
                f"Failed to find program '{program[0]}'", type="ERROR", colour="red"
            )
            return

    helpers.log("Preparing to build...")
    config_opts = {}
    if os.path.isfile(config_path):
        helpers.log("Found custom build configuration")
        with open(config_path, "r") as config_file:
            config_opts = json.load(config_file)
    else:
        helpers.log("Using default build configuration.")

    try:
        config = Config(**config_opts)
        config.adjust(build, sources, entry, libs)
        comp_list = get_comp_list(config) if compile else []
        execute(config, comp_list, debug, run)
    except FileNotFoundError as e:
        helpers.log(e, type="ERROR", colour="red")


if __name__ == "__main__":
    main(prog_name="jex")
