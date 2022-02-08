import json
import subprocess
import os
import hashlib

conv = lambda x: x.replace("\\", "/")
join = lambda x, y: conv(os.path.join(x, y))

BUF_SIZE = 65536 # 64Kb
BUILD = "./build"
META = join(BUILD, ".jexe")
SOURCES = "./src"
ENTRY = "Main"
CONFIG = "./jexe.json"
CLASSES = join(META, "classes")
HASHES = join(META, "classes.json")

print("Preparing to build...")
if os.path.isfile(CONFIG):
    print("Found custom build configuration")
    with open(CONFIG, "r") as metafile:
        metadata = json.load(metafile)
        BUILD = conv(metadata["build"])
        META = join(BUILD, ".jexe")
        SOURCES = conv(metadata["sources"])
        ENTRY = conv(metadata["entry"])
else:
    print("Using default build configuration.")

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
                    with open(name, 'rb') as f:
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

if recompile:
    print("Compiling...")
    subprocess.run(["javac", "-classpath", BUILD, f"@{CLASSES}", "-d", BUILD])

print(f"Running from: {ENTRY}")
subprocess.run(["java", "-cp", BUILD, ENTRY])