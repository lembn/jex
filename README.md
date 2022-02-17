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

## Usage With IDEs

Jex is designed to make Java development fast and lightweight, outside of an environment like IntelliJ or Eclipse, but some users may still want to use an IDE for writing code instead of just CLI tools or Notepad++. In this case, Jex recommends Visual Studio Code: a lightweight, versatlie IDE that will provide all the niceties of modern IDE development, with none of the extra hassle.

By nature, VSCode works directly on files and folders - without creating or requiring any extra metadata or project files to work out of the box. This is great because it will keep projects lightweight and independent from any overaching structure. VSCode is a general IDE that programmers can write any language in, so by default requires an extension to be installed to enhance the Java experience (don't worry, these won't effect your actual project files/structure in any way). Install [Language Support for Java(TM) by Red Hat](https://marketplace.visualstudio.com/items?itemName=redhat.java) into VSCode to provide linting, autocompletion and formatting support for Java. Then, in the root of the project, create a directory called `.vscode` and adda file to it called `settings.json`. Here we'll configure the settings for your project. Add following JSON entries to the file:

```json
{
  "java.format.settings.url": "https://raw.githubusercontent.com/google/styleguide/gh-pages/eclipse-java-google-style.xml",
  "java.project.referencedLibraries": ["lib/**/*.jar"]
}
```

- `"java.format.settings.url"` sets the formatter code style.
- `"java.project.referencedLibraries"` informs VSCode where the jar files for your external libraries are, allowing VSCode to provide autocompletion for your external libraries. This option is not required since Jex is completely seperate from VSCode and will still find your external libraries as long as you specify where they are.

These values can be adjusted to better suit your preferences and the structure of your project.

## Why Jex?

In all honesty, VSCode with its [Debugger for Java](https://marketplace.visualstudio.com/items?itemName=vscjava.vscode-java-debug) extension, could be used _completely_ in place of Jex, since it collects, compiles and executes code just like Jex does. Jex simply offers _another way_ to do the same thing, but in different environments (outside of an IDE). However if you don't care about other environments, Jex still contains many features VSCode debugger doesn't have:

- Initialsing projects
- Running tests
- Packaging projects into `.jar`
- Converting projects into BlueJ format

Furthermore, Jex provides complete transparency into what is actually happening to your code to get it to execute. The extreme lightweight design makes Jex great at quickly accomodating extensions in the functionality of your projects in a simple and intuitve way. For example, adding JavaFX to a Jex project doesn't require any extra extensions or complex configuration, just needs a quick and simple definition in the `jex.json` file. If any these are features that you're interested in, give Jex a try and see if you like it!

# Roadmap

- [ ] Fix debug mode
- [ ] Add init command
- [ ] Add test command
- [ ] Add convert to blueJ command
  - [ ] Enforce Java11
- [ ] Add build to jar command
