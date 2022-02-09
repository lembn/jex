import json
import subprocess
import os
import hashlib
import click

conv = lambda x: x.replace("\\", "/")
join = lambda x, y: conv(os.path.join(x, y))

BUF_SIZE = 65536  # 64Kb


def setup(path: str, config: dict):
    print("Preparing to build...")
    if os.path.isfile(path):
        print("Found custom build configuration")
        with open(path, "r") as config_file:
            metadata = json.load(config_file)
            BUILD = conv(metadata["build"])
            SOURCES = conv(metadata["sources"])
            ENTRY = conv(metadata["entry"])
    else:
        print("Using default build configuration.")


def prepare():
    if not os.path.exists(META):
        os.makedirs(META)
    if not os.path.exists(HASHES):
        with open(HASHES, "w") as hash_file:
            hash_file.write("{}")

    print("Collecting source files")
    recompile = False
    with open(HASHES, "r+") as hash_file:
        hashes = json.load(hash_file)
        filenames = []

        with open(CLASSES, "w") as classes_file:
            for root, _, files in os.walk(SOURCES):
                for name in files:
                    if ".java" in name:
                        name = join(root, name)
                        filenames.append(name)
                        md5 = hashlib.md5()
                        with open(name, "rb") as f:
                            while True:
                                data = f.read(BUF_SIZE)
                                if not data:
                                    break
                                md5.update(data)
                        file_hash = md5.hexdigest()
                        if name in hashes and hashes[name] == file_hash:
                            continue
                        print(f"Found updated file: {name}")
                        recompile = True
                        classes_file.write(f"{name}\n")
                        hashes[name] = file_hash

        hashes = {i: j for i, j in hashes.items() if i in filenames}
        hash_file.seek(0)
        hash_file.truncate()
        hash_file.write(json.dumps(hashes))


def run(compile: bool, run: bool):
    if compile:
        print("Compiling...")
        subprocess.run(["javac", "-classpath", BUILD, f"@{CLASSES}", "-d", BUILD])

    if run:
        print(f"Running from: {ENTRY}")
        subprocess.run(["java", "-cp", BUILD, ENTRY])


@click.command()
@click.option(
    "-c",
    "--config",
    default="./jexe.json",
    type=click.Path(dir_okay=False),
    help="Path to the 'jexe.json' configuration file.",
)
@click.option(
    "-b",
    "--build",
    default="./build",
    type=click.Path(file_okay=False),
    help="Directory path to compile to.",
)
@click.option(
    "-s",
    "--sources",
    default="./src",
    type=click.Path(file_okay=False),
    help="Path to the containing directory of the source code.",
)
@click.option(
    "-e",
    "--entry",
    default="Main",
    type=click.STRING,
    help="Java FQN of the entry point file.",
)
@click.option(
    "-d", "--debug", default=False, type=click.BOOL, help="Run in debug mode."
)
@click.option(
    "--compile/--no-compile",
    default=False,
    type=click.BOOL,
    help="Compile the project.",
)
@click.option("--run/--no-run", default=False, type=click.BOOL, help="Run the project.")
@click.option("--errors", default=False, type=click.BOOL, help="Show last errors.")
def main(
    config: str,
    build: str,
    sources: str,
    entry: str,
    debug: bool,
    compile: bool,
    run: bool,
    errors: bool,
):
    """
    A lightweight wrapper for the Java CLI programs to act as a build tool
    for fast development of complex projects in a simple environment.
    """

    META = join(build, ".jexe")
    CLASSES = join(META, "classes")
    HASHES = join(META, "classes.json")

    # TODO: check config opt actually points to a valid jexe.json
    setup(config)
    prepare()
    run()


if __name__ == "__main__":
    main(prog_name="jexe")
