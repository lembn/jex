# jexe

A lightweight wrapper for the Java CLI programs to act as a build tool for fast development of complex projects in a simple environment.

> An installation of Java is required on the system for this program to work.

## Build Configuration

Build configuration can be customised by creating a `jexe.json`, where certain attributes of the build process can be set.

```json
{
    "build": ...,
    "sources": ...,
    "entry": ...,
}
```

- `build` is the path of the directory that the source code should be compiled to.
- `sources` is the path of the lowest directory containing all of the source code.
- `entry` is the Java FQN of the entry point file.

These attributes can also be set in the tool directly, by passing them as command line options, when execute the program

## Roadmap

- [ ] Add support for command line args as well as config file (`jexe.json`)
  - [ ] Pass path to config file as argument, default value is root
- [ ] Better logging
  - [ ] Use `click.echo()` instead of `print()`
  - [ ] Format
  - [ ] Log to file
- [ ] Handle errors
  - [ ] Log compile-time errors, then quit (don't run)
  - [ ] Log run-time errors
  - [ ] Create flag that will show errors
  - [ ] Reset errors per build
- [ ] Debug mode
  - [ ] Call `jdb` instead of `java`
  - [ ] Debug binaries have to be compiled differently
- [ ] Create executable
  - [ ] Create release
