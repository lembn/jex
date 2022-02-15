# jex

A lightweight wrapper for the Java CLI programs to act as a build tool for fast development of complex projects in a simple environment.

> An installation of Java is required on the system for this program to work.

## Build Configuration

Build configuration can be customised by creating a `jex.json` file and pointing `jex` to the location of the file with the `--config-path` option. All these settings are optional, so they don't all need to be defined (they defaults will be used instead). Here is an example `jex.json` file, with the default settings:

```json
{
  "build": ...,
  "sources": ...,
  "entry": ...
}
```

```
Options:
Options:
  --version                 Show the version and exit.
  -c, --config-path FILE    Path to the 'jex.json' configuration file.
                            [default: ./jex.json]
  -b, --build DIRECTORY     Directory path to compile to. [default: ./build]
  -s, --sources DIRECTORY   Path to the containing directory of the source
                            code. [default: ./src]
  -e, --entry TEXT          Java FQN of the entry point file. [default: Main]
  -l, --libs DIRECTORY      Path to the containing directory of library files
                            (*.jar). This option has no default, if not
                            explicitly defined, no libaries will be passed to
                            the compiler.
  -d, --debug BOOLEAN       Run in debug mode.  [default: False]
  --compile / --no-compile  Compile the project.  [default: compile]
  --run / --no-run          Run the entry point `main` method.  [default: run]
  -si, --silent             Disable console logs.  [default: False]
  --help                    Show this message and exit.
```

> _Direcotry paths in `jex.json` should not include a traling `/`, for example: write `"build": "./build", not "build": "./build/"._

These attributes can also be set in the tool directly, by passing them as command line options when executing the program. Any specified command line options will override `jex.json` settings.

# TODO

- [ ] Fix debug mode
