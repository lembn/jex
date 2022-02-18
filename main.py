import json
import platform
import re
import shutil
import subprocess
import os
from typing import List
import click
import helpers
from config import Config, ConfigLoadError

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
    args = []

    sep = ";" if platform.system() == "Windows" else ":"
    if config.libs:
        helpers.log(f"LIBS - {config.libs}")
        classpaths = [config.build]
        classpaths.append(helpers.format_classpath(config.libs))
        for root, dirs, _ in os.walk(config.libs):
            for dir in dirs:
                classpaths.append(f"{helpers.join(root, dir)}/*")
        classpath = sep.join(classpaths)
    else:
        classpath = config.build

    module_args = []
    if config.module_paths:
        helpers.log(f"MODULE PATHS - {config.module_paths}")
        helpers.log(f"MODULES - {config.modules}")
        module_args += [
            "--module-path",
            sep.join(config.module_paths),
            "--add-modules",
            sep.join(config.modules),
        ]

    if compile:
        helpers.log("Compiling...")
        args = ["javac", "-classpath", classpath, "-d", config.build]
        if config.module_paths:
            args += module_args
        args += compile
        result = subprocess.run(args)

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

        args = [program, "-classpath", classpath]
        if config.module_paths:
            args += module_args
        args.append(config.entry)
        result = subprocess.run(args)

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
@click.version_option("1.5.2")
# The config options have no default so that their value will be None if they are
# not passed in the command line. This is done so that Config.adjust() will when
# it should or shouldn't overrdide file options
@click.option(
    "-n",
    "--name",
    default=Config.NAME_DEFAULT,
    show_default=True,
    type=click.STRING,
    help="The name of the configuration to run from the 'jex.json' file (if it exists).",
)
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
    type=click.Path(),
    help=f"Path to the containing directory of library files (*.jar). This option has no default, if not explicitly defined, no libaries will be passed to the compiler.",
)
@click.option(
    "-d",
    "--debug",
    is_flag=True,
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
    help="Disable console logs. Also disables error messages.",
)
@click.option(
    "-c",
    "--clean",
    is_flag=True,
    show_default=True,
    type=click.BOOL,
    help="Delete old jex data before building.",
)
def main(
    name: str,
    config_path: str,
    build: str,
    sources: str,
    entry: str,
    libs: str,
    debug: bool,
    compile: bool,
    run: bool,
    silent: bool,
    clean: bool,
) -> None:
    """
    A lightweight wrapper for the Java CLI programs to act as a build tool
    for fast development of complex projects in a simple environment.

    \b
    jex.json format:
    {
        "default": {
            "build": ...,
            "sources": ...,
            "entry": ...,
            "libs": ...,
            "modulePaths": ...,
            "modules": ...,
            "debug": ...
        },
        "debug": {
        ...
        }
    }

    NOTE: "modulePaths" and "modules" cannot be set by command line options,
    they must be specified in jex.json if they are being used.
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
    config = None
    if os.path.isfile(config_path):
        helpers.log("Found custom build configurations.")
        with open(config_path, "r") as config_file:
            try:
                names = name.split(".")
                configurations = json.load(config_file)
            except json.JSONDecodeError:
                helpers.log(
                    "Invalid Jex configuration file.", type="ERROR", colour="red"
                )
                return

        for config_name in names:
            configuration = configurations.get(config_name)

            if configuration == None:
                helpers.log(
                    f"No configuration found with name '{config_name}'.",
                    type="ERROR",
                    colour="red",
                )
                return

            for key in configuration.keys():
                if key not in Config.KEYS:
                    helpers.log(
                        f"Invalid Jex configuration option {key}.",
                        type="ERROR",
                        colour="red",
                    )
                    return

            try:
                if not config:
                    config = Config(**configuration)
                else:
                    config.adjust(**configuration)
            except FileNotFoundError as e:
                helpers.log(e, type="ERROR", colour="red")
                return
            except ConfigLoadError as e:
                helpers.log(e, type="ERROR", colour="red")
                return

        helpers.log(f"Using custom configuration '{name}'.")
        if config.silent or silent:
            helpers.set_silent()

        adjustment = {}
        if build:
            adjustment[Config.BUILD_KEY] = build
        if sources:
            adjustment[Config.SOURCES_KEY] = sources
        if entry:
            adjustment[Config.ENTRY_KEY] = entry
        if libs:
            adjustment[Config.LIBS_KEY] = libs
        config.adjust(**adjustment)
    else:
        helpers.log("Using default build configuration.")
        config = Config()

    if clean:
        if os.path.exists(config.build):
            shutil.rmtree(config.build)
    comp_list = get_comp_list(config) if compile else []
    execute(config, comp_list, debug, run)


if __name__ == "__main__":
    main(prog_name="jex")
