from distutils.dir_util import copy_tree
import glob
import json
import platform
import re
import shutil
import subprocess
import os
from typing import List
import click
import helpers
from config import Config


def get_updated(config: Config) -> tuple[List[str], List[str]]:
    """
    Get lists containing the filenames of tracked source and resouce files that
    have updated. Also updates the tracking files and prunes the build folder.
    """

    # Ensure jex files
    if not os.path.exists(config.meta):
        os.makedirs(config.meta)
    if not os.path.exists(config.class_hash):
        with open(config.class_hash, "w") as hash_file:
            hash_file.write("{}")
    if not os.path.exists(config.res_hash):
        with open(config.res_hash, "w") as hash_file:
            hash_file.write("{}")

    updated_src = []
    updated_res = []
    # The purpose of `processed_files` is to keep track of all the files that were scanned
    # in this run. This way we can detect if files have been deleted from the source folder
    # becasue they will be present in `hashes` (from the last run) but not present in `processed_files`
    processed_files = []

    # Collect source files
    helpers.log("Collecting source files...")
    with open(config.class_hash, "r+") as hash_file:
        hashes = json.load(hash_file)
        # Find updated files
        for root, _, files in os.walk(config.sources):
            for name in files:
                if ".java" in name:
                    name = helpers.join(root, name)
                    processed_files.append(name)
                    file_hash = helpers.hash_file(name)
                    bin_path = config.transform(name, True)
                    if helpers.updated(name, hashes, file_hash, bin_path):
                        helpers.log(f"Found updated source file: {name}")
                        updated_src.append(name)
                        hashes[name] = file_hash

        # Prune artefacts
        hashes = {i: j for i, j in hashes.items() if i in processed_files}
        for root, dirs, files in os.walk(config.build):
            for name in files:
                if ".class" in name:
                    if "$" in name:
                        name = re.sub(r"\$.*", ".class", name)
                    name = helpers.join(root, name)
                    src_name = config.transform(name, False)
                    if src_name not in hashes:
                        os.remove(name)
            helpers.prune(root, dirs)
        helpers.overwrite(hash_file, json.dumps(hashes))

    # Collect resources
    processed_files = []
    if config.resources:
        helpers.log("Collecting resources...")
        with open(config.res_hash, "r+") as hash_file:
            hashes = json.load(hash_file)
            # Find updated files
            for root, _, files in os.walk(config.resources):
                for name in files:
                    name = helpers.join(root, name)
                    processed_files.append(name)
                    file_hash = helpers.hash_file(name)
                    bin_path = config.transform(name, True)
                    if helpers.updated(name, hashes, file_hash, bin_path):
                        helpers.log(f"Found updated resource: {name}")
                        hashes[name] = file_hash
                        updated_res.append(name)

            # Prune artefacts
            hashes = {i: j for i, j in hashes.items() if i in processed_files}
            res_build = config.transform(config.resources, True)
            for root, dirs, files in os.walk(res_build):
                for name in files:
                    name = helpers.join(root, name)
                    src_name = config.transform(name, False)
                    if src_name not in hashes:
                        os.remove(name)
                helpers.prune(root, dirs)
            helpers.overwrite(hash_file, json.dumps(hashes))

    return updated_src, updated_res


def execute(
    config: Config, updated_src: List[str], updated_res: List[str], debug: bool
) -> None:
    opened = False
    bar = "===========================================\n"
    args = []

    print()
    sep = ";" if platform.system() == "Windows" else ":"
    if config.libs:
        helpers.log(f"LIBS - {config.libs}")
        classpaths = [config.build]
        ignore = []
        for ex in config.exclude_libs:
            globbed = glob.glob(ex, recursive=True)
            ignore += list(map(lambda x: helpers.conv(x), globbed))
        for root, dirs, _ in os.walk(config.libs):
            for dir in dirs:
                dir_path = helpers.join(root, dir)
                jars = [d for d in os.listdir(dir_path) if d.endswith(".jar")]
                if dir_path not in ignore and len(jars) > 0:
                    classpaths.append(dir_path + "/*")
        classpath = sep.join(classpaths)
    else:
        classpath = config.build

    helpers.log(f"IGNORED - {ignore}")
    module_args = []
    if config.module_paths:
        helpers.log(f"MODULE PATHS - {config.module_paths}")
        helpers.log(f"MODULES - {config.modules}")
        module_args += [
            "--module-path",
            sep.join(config.module_paths),
            "--add-modules",
            ",".join(config.modules),
        ]

    if updated_src:
        helpers.log("Compiling...")
        args = ["javac", "-classpath", classpath, "-d", config.build]
        if config.module_paths:
            args += module_args
        args += updated_src
        helpers.log(args)
        result = subprocess.run(args)

        if result.stderr:
            opened = True
            with open(config.errors, "a") as err_file:
                err_file.writelines(
                    [bar, helpers.time() + "\n", result.stderr], bar + "\n"
                )
            helpers.log(
                f"Occurred during compilation, check {os.path.abspath(config.errors)} for info.",
                type="ERROR",
                colour="red",
            )
            os.remove(config.class_hash)

            return
    if updated_res:
        for res in updated_res:
            target = config.transform(res, True)
            target_dir = os.path.dirname(target)
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            shutil.copyfile(res, target)

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
    helpers.log(args)
    result = subprocess.run(args)

    if result.stderr:
        with open(config.errors, "a") as err_file:
            if not opened:
                err_file.writelines([bar, helpers.time() + "\n"])
                opened = True
            err_file.writelines([result.stderr, bar + "\n"])
        helpers.log(
            f"Occurred during execution, check {os.path.abspath(config.errors)} for info.",
            type="ERROR",
            colour="red",
        )


@click.command()
@click.version_option("1.6.0")
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
    type=click.Path(exists=True, file_okay=False),
    help=f"Path to the containing directory of library files (*.jar). This option has no default, if not explicitly defined, no libaries will be passed to the compiler.",
)
@click.option(
    "-r",
    "--resources",
    type=click.Path(exists=True, file_okay=False),
    help=f"Path to the project's resources directory. Must be located within the sources directory.",
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
    resources: str,
    debug: bool,
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
            "excludeLibs": ...,
            "modulePaths": ...,
            "modules": ...,
            "resources": ...
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
            except helpers.ConfigLoadError as e:
                helpers.log(e, type="ERROR", colour="red")
                return

        helpers.log(f"Using custom configuration '{name}'.")
        if config.silent or silent:
            helpers.set_silent()

        adjustment = {
            Config.SILENT_KEY: silent,
            Config.DEBUG_KEY: debug,
            Config.CLEAN_KEY: clean,
        }
        if build:
            adjustment[Config.BUILD_KEY] = build
        if sources:
            adjustment[Config.SOURCES_KEY] = sources
        if entry:
            adjustment[Config.ENTRY_KEY] = entry
        if libs:
            adjustment[Config.LIBS_KEY] = libs
        if resources:
            adjustment[Config.RESOURCES_KEY] = resources
        config.adjust(**adjustment)
    else:
        helpers.log("Using default build configuration.")
        config = Config()

    if clean:
        if os.path.exists(config.build):
            shutil.rmtree(config.build)
    updated_src, updated_res = get_updated(config)
    execute(config, updated_src, updated_res, debug)


if __name__ == "__main__":
    main(prog_name="jex")
