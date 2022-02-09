import helpers


class Config:
    BUILD_KEY = "build"
    BUILD_DEFAULT = "./build"
    SOURCES_KEY = "sources"
    SOURCES_DEFAULT = "./src"
    ENTRY_KEY = "entry"
    ENTRY_DEFAULT = "Main"

    def __init__(
        self,
        build: str,
        sources: str,
        entry: str,
    ):
        self.build = helpers.conv(build)
        self.sources = helpers.conv(sources)
        self.entry = helpers.conv(entry)
        self.meta = helpers.join(self.build, ".jexe")
        self.classes = helpers.join(self.meta, "classses")
        self.hashes = helpers.join(self.meta, "classses.json")

    def getDict(build, sources, entry) -> dict:
        return {
            Config.BUILD_KEY: build,
            Config.SOURCES_KEY: sources,
            Config.ENTRY_KEY: entry,
        }
