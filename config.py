import helpers

# TODO: validated resources exists
# TODO: validated resources is dir
# TODO: validated resources is sub of sources


class Config:
    JEX = ".jex"

    BUILD_KEY = "build"
    SOURCES_KEY = "sources"
    ENTRY_KEY = "entry"
    SILENT_KEY = "silent"
    DEBUG_KEY = "debug"
    CLEAN_KEY = "clean"
    LIBS_KEY = "libs"
    EXCLUDE_KEY = "excludeLibs"
    MODULE_PATHS_KEY = "modulePaths"
    MODULES_KEY = "modules"
    RESOURCES_KEY = "resources"

    NAME_DEFAULT = "default"
    BUILD_DEFAULT = "./build"
    SOURCES_DEFAULT = "./src"
    ENTRY_DEFAULT = "Main"
    SILENT_DEFAULT = False
    DEBUG_DEFAULT = False
    CLEAN_DEFAULT = False
    EXCLUDE_DEFAULT = []

    KEYS = [
        BUILD_KEY,
        SOURCES_KEY,
        ENTRY_KEY,
        SILENT_KEY,
        DEBUG_KEY,
        CLEAN_KEY,
        LIBS_KEY,
        EXCLUDE_KEY,
        MODULE_PATHS_KEY,
        MODULES_KEY,
        RESOURCES_KEY,
    ]

    def __init__(self, **kwargs: str):
        self.set_build(kwargs.get(Config.BUILD_KEY, Config.BUILD_DEFAULT), True)
        self.sources = kwargs.get(Config.SOURCES_KEY, Config.SOURCES_DEFAULT)
        self.entry = helpers.conv(kwargs.get(Config.ENTRY_KEY, Config.ENTRY_DEFAULT))
        self.silent = kwargs.get(Config.SILENT_KEY, Config.SILENT_DEFAULT)
        self.debug = kwargs.get(Config.DEBUG_KEY, Config.DEBUG_DEFAULT)
        self.clean = kwargs.get(Config.CLEAN_KEY, Config.CLEAN_DEFAULT)
        self.libs = kwargs.get(Config.LIBS_KEY)
        if self.libs:
            helpers.validate_array(self.libs, Config.LIBS_KEY)
            self.libs = list(map(lambda x: helpers.conv(x), self.libs))
        self.exclude_libs = kwargs.get(Config.EXCLUDE_KEY, [])
        if self.exclude_libs:
            helpers.validate_array(
                self.exclude_libs, Config.EXCLUDE_KEY, allow_empty=True
            )
            self.exclude_libs = list(map(lambda x: helpers.conv(x), self.exclude_libs))
        self.module_paths = kwargs.get(Config.MODULE_PATHS_KEY)
        if not self.module_paths == None:
            helpers.validate_array(self.module_paths, Config.MODULE_PATHS_KEY)
            self.module_paths = list(
                map(lambda x: helpers.safe_conv(x), self.module_paths)
            )
            self.modules = kwargs.get(Config.MODULES_KEY)
            if not self.modules == None:
                helpers.validate_array(self.modules, Config.MODULES_KEY)
            else:
                raise helpers.ConfigLoadError(
                    f"'{Config.MODULES_KEY}' must be defined if '{Config.MODULE_PATHS_KEY}' is defined."
                )
        else:
            self.modules = None
        self.resources = kwargs.get(Config.RESOURCES_KEY)

    def adjust(self, **kwargs: str):
        self.set_build(kwargs.get(Config.BUILD_KEY, self.build), False)
        self.sources = helpers.safe_conv(kwargs.get(Config.SOURCES_KEY, self.sources))
        self.entry = helpers.conv(kwargs.get(Config.ENTRY_KEY, self.entry))
        self.silent = kwargs.get(Config.SILENT_KEY, self.silent)
        self.debug = kwargs.get(Config.DEBUG_KEY, self.debug)
        self.clean = kwargs.get(Config.CLEAN_KEY, self.clean)

    def set_build(self, build: str, init: bool) -> None:
        if not init and build == self.build:
            return
        self.build = helpers.conv(build)
        self.meta = helpers.join(self.build, Config.JEX)
        self.class_hash = helpers.join(self.meta, "classes.json")
        self.res_hash = helpers.join(self.meta, "resources.json")
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
