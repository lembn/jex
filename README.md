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

- [ ] Ignore commented lines (at the moment comments will cause re-compilation)
- [ ] Add support for command line args as well as config file (`jexe.json`)
  - [ ] Pass path to config file as argument, default value is root
- [ ] Create executable
  - [ ] Create release
