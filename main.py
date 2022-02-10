import json
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
                        if name in hashes and hashes[name] == file_hash:
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


def execute(config: Config, compile: bool, run: bool) -> None:
    if compile:
        helpers.log("Compiling...")
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
        helpers.log(f"Running from: {config.entry}")
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
    execute(config, compile, run)


if __name__ == "__main__":
    main(prog_name="jexe")
