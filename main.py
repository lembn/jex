import json
import subprocess
import os
import click
import helpers
from config import Config


def setup(config_path: str, config: dict) -> Config:
    if os.path.isfile(config_path):
        print("Found custom build configuration")
        with open(config_path, "r") as config_file:
            config = json.load(config_file)
    else:
        print("Using default build configuration.")

    build = (
        config[Config.BUILD_KEY] if Config.BUILD_KEY in config else Config.BUILD_DEFAULT
    )
    sources = (
        config[Config.SOURCES_KEY]
        if Config.SOURCES_KEY in config
        else Config.SOURCES_DEFAULT
    )
    entry = (
        config[Config.ENTRY_KEY] if Config.ENTRY_KEY in config else Config.ENTRY_DEFAULT
    )

    return Config(build, sources, entry)


def prepare(config: Config) -> None:
    if not os.path.exists(config.meta):
        os.makedirs(config.meta)
    if not os.path.exists(config.hashes):
        with open(config.hashes, "w") as hash_file:
            hash_file.write("{}")

    print("Collecting source files")
    compile = False
    with open(config.hashes, "r+") as hash_file:
        hashes = json.load(hash_file)
        filenames = []

        with open(config.classes, "w") as classes_file:
            for root, _, files in os.walk(config.classes):
                for name in files:
                    if ".java" in name:
                        name = helpers.join(root, name)
                        filenames.append(name)
                        file_hash = helpers.hash_file(name)
                        if name in hashes and hashes[name] == file_hash:
                            continue
                        print(f"Found updated file: {name}")
                        compile = True
                        classes_file.write(f"{name}\n")
                        hashes[name] = file_hash

        hashes = {i: j for i, j in hashes.items() if i in filenames}
        hash_file.seek(0)
        hash_file.truncate()
        hash_file.write(json.dumps(hashes))

        return compile


def run(config: Config, compile: bool, run: bool) -> None:
    if compile:
        print("Compiling...")
        subprocess.run(
            [
                "javac",
                "-classpath",
                config.build,
                f"@{config.classes}",
                "-d",
                config.build,
            ]
        )

    if run:
        print(f"Running from: {config.entry}")
        subprocess.run(["java", "-cp", config.build, config.entry])


@click.command()
@click.option(
    "-c",
    "--config-path",
    default="./jexe.json",
    type=click.Path(dir_okay=False),
    help="Path to the 'jexe.json' configuration file.",
)
@click.option(
    "-b",
    "--build",
    type=click.Path(file_okay=False),
    help="Directory path to compile to.",
)
@click.option(
    "-s",
    "--sources",
    type=click.Path(file_okay=False),
    help="Path to the containing directory of the source code.",
)
@click.option(
    "-e",
    "--entry",
    type=click.STRING,
    help="Java FQN of the entry point file.",
)
@click.option(
    "-d", "--debug", default=False, type=click.BOOL, help="Run in debug mode."
)
@click.option(
    "--compile/--no-compile",
    default=True,
    type=click.BOOL,
    help="Compile the project.",
)
@click.option("--run/--no-run", default=True, type=click.BOOL, help="Run the project.")
@click.option("--errors", default=False, type=click.BOOL, help="Show last errors.")
def main(
    config_path: str,
    build: str,
    sources: str,
    entry: str,
    debug: bool,
    compile: bool,
    run: bool,
    errors: bool,
) -> None:
    """
    A lightweight wrapper for the Java CLI programs to act as a build tool
    for fast development of complex projects in a simple environment.
    """

    print("Preparing to build...")
    config = setup(config_path, Config.getDict(build, sources, entry))
    if compile:
        compile = prepare(config)
    run(config, compile, run)


if __name__ == "__main__":
    main(prog_name="jexe")
