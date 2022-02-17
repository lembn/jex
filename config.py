import os
import helpers

# TODO: validate that modulePaths and modules are arrays
# TODO: make sure that modulePaths exists with modules
# TODO: make sure that modules exists with modulePaths


class ConfigLoadError(Exception):
    pass


class Config:
    BUILD_KEY = "build"
    BUILD_DEFAULT = "./build"
    SOURCES_KEY = "sources"
    SOURCES_DEFAULT = "./src"
    ENTRY_KEY = "entry"
    ENTRY_DEFAULT = "Main"
    LIBS_KEY = "lib"
    MODULE_PATHS_KEY = "modulePaths"
    MODULES_KEY = "modules"

    KEYS = [
        BUILD_KEY,
        SOURCES_KEY,
        ENTRY_KEY,
        LIBS_KEY,
        MODULE_PATHS_KEY,
        MODULES_KEY,
    ]

    def path_exists(path: str, default: str = None, strict: bool = False) -> None:
        if not path and not strict:
            return default
        else:
            if not os.path.exists(path):
                raise ConfigLoadError(
                    f"The path '{path}' provided from configuration file does not exist."
                )
            else:
                return helpers.conv(path)

    def __init__(self, **kwargs: str):
        self.set_build(kwargs.get(Config.BUILD_KEY, Config.BUILD_DEFAULT))
        self.sources = Config.path_exists(
            kwargs.get(Config.SOURCES_KEY), default=Config.SOURCES_DEFAULT
        )
        self.entry = helpers.conv(kwargs.get(Config.ENTRY_KEY, Config.ENTRY_DEFAULT))
        self.libs = Config.path_exists(kwargs.get(Config.LIBS_KEY))

        module_paths = kwargs.get(Config.MODULE_PATHS_KEY)
        modules = kwargs.get(Config.MODULES_KEY)
        if not isinstance(module_paths, list):
            raise ConfigLoadError("Invalid modulePaths. Must be an array.")
        if module_paths == []:
            raise ConfigLoadError("If modulePaths is specified it cannot be empty.")
        else:
            self.module_paths = map(
                lambda x: Config.path_exists(x, strict=True), module_paths
            )
        if not isinstance(modules, list):
            raise ConfigLoadError("Invalid modulePaths. Must be an array.")
        if modules == []:
            raise ConfigLoadError("If modules is specified it cannot be empty.")
        else:
            self.module_paths = modules

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
