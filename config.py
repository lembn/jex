import os
import helpers


class ConfigLoadError(Exception):
    pass


class Config:
    BUILD_KEY = "build"
    SOURCES_KEY = "sources"
    ENTRY_KEY = "entry"
    SILENT_KEY = "silent"
    LIBS_KEY = "lib"
    MODULE_PATHS_KEY = "modulePaths"
    MODULES_KEY = "modules"

    BUILD_DEFAULT = "./build"
    SOURCES_DEFAULT = "./src"
    ENTRY_DEFAULT = "Main"
    SILENT_DEFAULT = False

    KEYS = [
        BUILD_KEY,
        SOURCES_KEY,
        ENTRY_KEY,
        SILENT_KEY,
        LIBS_KEY,
        MODULE_PATHS_KEY,
        MODULES_KEY,
    ]

    def __init__(self, **kwargs: str):
        self.set_build(kwargs.get(Config.BUILD_KEY, Config.BUILD_DEFAULT))
        self.sources = kwargs.get(Config.SOURCES_KEY, Config.SOURCES_DEFAULT)
        self.entry = helpers.conv(kwargs.get(Config.ENTRY_KEY, Config.ENTRY_DEFAULT))
        self.silent = kwargs.get(Config.SILENT_KEY, Config.SILENT_DEFAULT)
        self.libs = Config.safe_conv(kwargs.get(Config.LIBS_KEY))
        self.module_paths = kwargs.get(Config.MODULE_PATHS_KEY)
        if not self.module_paths == None:
            if not isinstance(self.module_paths, list):
                raise ConfigLoadError("Invalid 'modulePaths' - must be an array.")
            if self.module_paths == []:
                raise ConfigLoadError(
                    "If 'modulePaths' is specified it cannot be empty."
                )
            else:
                self.module_paths = map(
                    lambda x: helpers.safe_conv(x), self.module_paths
                )
            self.modules = kwargs.get(Config.MODULES_KEY)
            if not self.modules == None:
                if not isinstance(self.modules, list):
                    raise ConfigLoadError("Invalid 'modules' - must be an array.")
                if self.modules == []:
                    raise ConfigLoadError(
                        "If 'modules' is specified it cannot be empty."
                    )
                else:
                    self.modules = self.modules
            else:
                raise ConfigLoadError(
                    "'modules' must be defined if 'modulePaths' is defined."
                )
        else:
            self.modules = None

    def adjust(self, **kwargs: str):
        self.set_build(kwargs.get(Config.BUILD_KEY, self.build))
        self.sources = helpers.safe_conv(kwargs.get(Config.SOURCES_KEY, self.sources))
        self.entry = helpers.conv(kwargs.get(Config.ENTRY_KEY, self.entry))
        self.silent = kwargs.get(Config.SILENT_KEY, self.silent)
        self.libs = helpers.safe_conv(kwargs.get(Config.LIBS_KEY, self.libs))
        self.module_paths = kwargs.get(Config.MODULE_PATHS_KEY)
        if not self.module_paths == None:
            if not isinstance(self.module_paths, list):
                raise ConfigLoadError("Invalid 'modulePaths' - must be an array.")
            if self.module_paths == []:
                raise ConfigLoadError(
                    "If 'modulePaths' is specified it cannot be empty."
                )
            else:
                self.module_paths = map(
                    lambda x: helpers.safe_conv(x), self.module_paths
                )
            self.modules = kwargs.get(Config.MODULES_KEY)
            if not self.modules == None:
                if not isinstance(self.modules, list):
                    raise ConfigLoadError("Invalid 'modules' - must be an array.")
                if self.modules == []:
                    raise ConfigLoadError(
                        "If 'modules' is specified it cannot be empty."
                    )
                else:
                    self.modules = self.modules
            else:
                raise ConfigLoadError(
                    "'modules' must be defined if 'modulePaths' is defined."
                )

    def set_build(self, build: str) -> None:
        if build == self.build:
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
