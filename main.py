import json
import re
import subprocess
import os
import click
import helpers
from config import Config


def prepare(config: Config) -> bool:
    if not os.path.exists(config.meta):
        os.makedirs(config.meta)
    if not os.path.exists(config.hashes):
        with open(config.hashes, "w") as hash_file:
            hash_file.write("{}")

    helpers.log("Collecting source files")
    compile = False
    with open(config.hashes, "r+") as hash_file:
        hashes = json.load(hash_file)
        filenames = []

        with open(config.classes, "w") as classes_file:
            for root, _, files in os.walk(config.sources):
                for name in files:
                    if ".java" in name:
                        name = helpers.join(root, name)
                        filenames.append(name)
                        file_hash = helpers.hash_file(name)
                        name_ = re.sub(r"(\./)", "", name)
                        name_ = re.sub(".java", ".class", name_)
                        bin_path = helpers.join(config.build, name_)
                        if (
                            name in hashes
                            and hashes[name] == file_hash
                            and os.path.exists(bin_path)
                        ):
                            continue
                        helpers.log(f"Found updated file: {name}")
                        compile = True
                        classes_file.write(f"{name}\n")
                        hashes[name] = file_hash

        hashes = {i: j for i, j in hashes.items() if i in filenames}
        for root, dirs, files in os.walk(config.build):
            for name in files:
                if ".class" in name:
                    name = helpers.join(root, name)
                    src_name = config.get_src_path(name.replace(".class", ".java"))
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


def execute(
    config: Config, compile: bool, debug: bool, run: bool, output: bool
) -> None:
    opened = False
    bar = "===========================================\n"
    if compile:
        helpers.log("Compiling...")
        result = subprocess.run(
            [
                "javac",
                "-classpath",
                config.build,
                f"@{config.classes}",
                "-d",
                config.build,
            ],
            capture_output=True,
            text=True,
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

    if run:
        program = "java"
        if debug:
            program = "jdb"
            helpers.log("DEBUG", colour="blue")
        helpers.log(f"Running from - {config.entry}")
        result = subprocess.run(
            [program, "-classpath", config.build, config.entry],
            capture_output=True,
            text=True,
        )
        if output and result.stdout:
            with open(config.output, "a") as out_file:
                out_file.writelines([bar, helpers.time(), result.stdout, bar, ""])
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
@click.version_option("1.0.5")
@click.option(
    "-c",
    "--config-path",
    default="./jexe.json",
    show_default=True,
    type=click.Path(dir_okay=False),
    help="Path to the 'jexe.json' configuration file.",
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
    type=click.Path(file_okay=False),
    help=f"Path to the containing directory of the source code. [default: {Config.SOURCES_DEFAULT}]",
)
@click.option(
    "-e",
    "--entry",
    type=click.STRING,
    help=f"Java FQN of the entry point file. [default: {Config.ENTRY_DEFAULT}]",
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
@click.option(
    "-o",
    "--output",
    is_flag=True,
    show_default=True,
    type=click.BOOL,
    help="Capture execution output.",
)
def main(
    config_path: str,
    build: str,
    sources: str,
    entry: str,
    debug: bool,
    compile: bool,
    run: bool,
    silent: bool,
    output: bool,
) -> None:
    """
    A lightweight wrapper for the Java CLI programs to act as a build tool
    for fast development of complex projects in a simple environment.
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

    config = Config(**config_opts)
    config.set_build(build)
    config.set_sources(sources)
    config.set_entry(entry)

    if compile:
        compile = prepare(config)
    execute(config, compile, debug, run, output)


if __name__ == "__main__":
    main(prog_name="jexe")
