import os
import helpers


class Config:
    BUILD_KEY = "build"
    BUILD_DEFAULT = "./build"
    SOURCES_KEY = "sources"
    SOURCES_DEFAULT = "./src"
    ENTRY_KEY = "entry"
    ENTRY_DEFAULT = "Main"
    LIB_KEY = "lib"

    def path_exists(path: str, default: str = None) -> None:
        if not path:
            return default
        else:
            if not os.path.exists(path):
                raise FileNotFoundError(f"The directory '{path}' provided from configuration file does not exist.")
            else:
                return path

    def __init__(self, **kwargs: dict[str, str]):
        self.set_build(kwargs.get(Config.BUILD_KEY, Config.BUILD_DEFAULT))
        self.sources = Config.path_exists(kwargs.get(Config.SOURCES_KEY), Config.SOURCES_DEFAULT)
        self.entry = helpers.conv(kwargs.get(Config.ENTRY_KEY, Config.ENTRY_DEFAULT))
        self.libs = Config.path_exists(kwargs.get(Config.LIB_KEY))

    def adjust(self, build: str, sources: str, entry: str, libs: str):
        self.set_build(build)
        self.sources = helpers.conv(sources) if sources else self.sources
        self.entry = helpers.conv(entry) if entry else self.entry
        self.libs = helpers.conv(libs) if libs else self.libs

    def set_build(self, build: str) -> None:
        if not build:
            return
        self.build = helpers.conv(build)
        self.meta = helpers.join(self.build, ".jex")
        self.classes = helpers.join(self.meta, "classes.json")
        self.errors = helpers.join(self.meta, "errors.txt")

    def transform(self, path: str, src_to_build: bool) -> str:
        current_ext, target_ext = (
            (".java", ".class") if src_to_build else (".class", ".java")
        )
        current_dir, target_dir = (
            (self.sources, self.build) if src_to_build else (self.build, self.sources)
        )
        path = path.replace(current_ext, target_ext)
        path = path.replace(current_dir, target_dir, 1)
        return path
