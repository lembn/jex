import helpers


class Config:
    BUILD_KEY = "build"
    BUILD_DEFAULT = "./build"
    SOURCES_KEY = "sources"
    SOURCES_DEFAULT = "./src"
    ENTRY_KEY = "entry"
    ENTRY_DEFAULT = "Main"

    def __init__(self, **kwargs):
        self.set_build(kwargs.get(Config.BUILD_KEY, Config.BUILD_DEFAULT))
        self.sources = helpers.conv(
            kwargs.get(Config.SOURCES_KEY, Config.SOURCES_DEFAULT)
        )
        self.entry = helpers.conv(kwargs.get(Config.ENTRY_KEY, Config.ENTRY_DEFAULT))

    def set_build(self, build: str) -> None:
        if not build:
            return
        self.build = helpers.conv(build)
        self.meta = helpers.join(self.build, ".jexe")
        self.classes = helpers.join(self.meta, "classes")
        self.hashes = helpers.join(self.meta, "classes.json")
        self.errors = helpers.join(self.meta, "errors.txt")

    def set_sources(self, sources: str) -> None:
        if not sources:
            return
        self.sources = helpers.conv(sources)

    def set_entry(self, entry: str) -> None:
        if not entry:
            return
        self.entry = helpers.conv(entry)

    def get_src_path(self, original: str) -> str:
        return original.replace(self.build, self.sources)
