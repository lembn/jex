# jex

A lightweight wrapper for the Java CLI programs to act as a build tool for fast development of complex projects in a simple environment.

> An installation of Java is required on the system for this program to work.

## Build Configuration

Build configuration can be customised by creating a `jex.json` file and pointing `jex` to the location of the file with the `--config-path` option. All these settings are optional, so they don't all need to be defined (they defaults will be used instead). Here is an example `jex.json` file, with the default settings:

```json
{
  "default": {
    "build": ...,
    "sources": ...,
    "entry": ...,
    "libs": ...,
    "resources": ...,
    "excludeLibs": ...,
    "modulePaths": ...,
    "modules": ...
  },
  "debug": {
    ...
  }
}
```

> _NOTE: `"modulePaths"` and `"modules"` cannot be set by command line options, they must be specified in jex.json if they are being used._

A `jex.json` file can define multiple configurations. Users can select these configurations with the `--name` command when calling the `jex` CLI. `"default"` is a special configuration name that serves as the default configuration, allowing users to use that configuration without explicitly specifying it as an option. If you call `jex` with no `--name` option and, it will find and load the `"default"` configuration in `jex.json` (if `jex.json` exists). Configurations can also be overridden. If `jex` is called with `--name a.b`, the configuration `"a"` will first be loaded, then it will be overriden by the settings in `"b"`.

These attributes can also be set in the tool directly, by passing them as command line options when executing the program. Any specified command line options will override `jex.json` settings:

```
Options:
  --version                 Show the version and exit.
  -n, --name TEXT           The name of the configuration to run from the
                            'jex.json' file (if it exists).  [default:
                            defualt]
  -c, --config-path FILE    Path to the 'jex.json' configuration file.
                            [default: ./jex.json]
  -b, --build DIRECTORY     Directory path to compile to. [default: ./build]
  -s, --sources DIRECTORY   Path to the containing directory of the source
                            code. [default: ./src]
  -e, --entry TEXT          Java FQN of the entry point file. [default: Main]
  -l, --libs PATH           Path to the containing directory of library files
                            (*.jar). This option has no default, if not
                            explicitly defined, no libaries will be passed to
                            the compiler.
  -d, --debug               Run in debug mode.  [default: False]
  --compile / --no-compile  Compile the project.  [default: compile]
  --run / --no-run          Run the entry point `main` method.  [default: run]
  -si, --silent             Disable console logs. Also disables error
                            messages.  [default: False]
  -c, --clean               Delete old jex data before building.  [default:
                            False]
  --help                    Show this message and exit.
```

This also means that `jex.json` configuration files are not madatory, but are recommended for complex projects, since it allows different environments to be quickly configured and swapped out (eg: release, debug, testing).

> _Direcotry paths in `jex.json` should not include a traling `/`, for example: write `"build": "./build", not "build": "./build/"._

## Usage With IDEs

Jex is designed to make Java development fast and lightweight, outside of an environment like IntelliJ or Eclipse, but some users may still want to use an IDE for writing code instead of just CLI tools or Notepad++. In this case, Jex recommends Visual Studio Code: a lightweight, versatlie IDE that will provide all the niceties of modern IDE development, with none of the extra hassle.

By nature, VS Code works directly on files and folders - without creating or requiring any extra metadata or project files to work out of the box. This is great because it will keep projects lightweight and independent from any overaching structure. VS Code is a general IDE that programmers can write any language in, so by default requires an extension to be installed to enhance the Java experience (don't worry, these won't effect your actual project files/structure in any way). Install [Language Support for Java(TM) by Red Hat](https://marketplace.visualstudio.com/items?itemName=redhat.java) into VS Code to provide linting, autocompletion and formatting support for Java. Then, in the root of the project, create a directory called `.VS Code` and adda file to it called `settings.json`. Here we'll configure the settings for your project. Add following JSON entries to the file:

```json
{
  "java.format.settings.url": "https://raw.githubusercontent.com/google/styleguide/gh-pages/eclipse-java-google-style.xml",
  "java.project.referencedLibraries": {
    "include": ["lib/**/*.jar"],
    "sources": {
      "PATH/TO/JAR.jar": "PATH/TO/SOURCE/ZIP.zip",
      ...,
    }
  }
}
```

- `"java.format.settings.url"` sets the formatter code style.
- `"java.project.referencedLibraries"` informs VS Code where the jar files for your external libraries are, allowing VS Code to provide autocompletion for your external libraries. This option is not required since Jex is completely seperate from VS Code and will still find your external libraries as long as you specify where they are.
- `"include"` is a glob pattern, pointing VS Code to the locations of your jar files (there is also an `"exclude"` option if you want VS Code to ignore )
- `"sources"` is a key value mapping, pointing VS Code to the source code archives for a given `.jar` file, allowing Javadocs from those source files to be displayed in the IDE [on hover](https://i.stack.imgur.com/bqlRi.png).

> _"By default, a referenced {binary}.jar will try to search {binary}-sources.jar under the same directory, and attach it as source if one match is found."_
> From [VS Code Documentation](https://code.visualstudio.com/docs/java/java-project).

This means that source archives only need to be added to the `"sources"` mapping if VS Code can't find them with its default behaviour.
To use Jex in VS Code, open VS Code's intergrated terminal, and everything in Jex can be done from there.

## Why Jex?

In all honesty, VS Code with its [Debugger for Java](https://marketplace.visualstudio.com/items?itemName=vscjava.VS Code-java-debug) extension, could be used _completely_ in place of Jex, since it collects, compiles and executes code just like Jex does. Jex simply offers _another way_ to do the same thing, but in different environments (outside of an IDE). However if you don't care about other environments, Jex still contains many features VS Code debugger doesn't have:

- Initialsing projects
- Running tests
- Packaging projects into `.jar`
- Converting projects into BlueJ format

Furthermore, Jex provides complete transparency into what is actually happening to your code to get it to execute. The extreme lightweight design makes Jex great at quickly accomodating extensions in the functionality of your projects in a simple and intuitve way. For example, adding JavaFX to a VS Code Java project rqeuires:

1. VS Code project manager for java to be installed,
2. then the libraries have to be referenced in the project manager,
3. then the VS Code debugger has to be reconfigured to inject the modules into the JVM.

Even then the process can be difficult since some complex VS Code stuff has to happen under the hood to make everything work, so when stuff goes wrong it can be a debugging nightmare. Jex doesn't require any extra extensions or complex configuration, the whole process can be done with just two extra entries in the `jex.json` file. If any these features sound interesting, give Jex a try and see if you like it!

## TODO

- How well does unit testing work with current Jex?
  - Should we add a testing mode?
- Does it work with no settings and no CLI options

# Roadmap

- [ ] Convert `--compile` into subcommand
- [ ] Add build to jar command
- [ ] Add convert to blueJ command?
  - [ ] Enforce Java11
- [ ] Add init command
  - Generate structure
  - Add README to lib folder
