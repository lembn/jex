# jexe

A lightweight wrapper for the Java CLI programs to act as a build tool for fast development of complex projects in a simple environment.

> An installation of Java is required on the system for this program to work.

## Build Configuration

Build configuration can be customised by creating a `jexe.json` file in the root directory of the projects. Here, certain attributes of the build tool can be set.

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

## TODO

- [] Ignore commented lines (at the moment comments will cause re-compilation)
- [] Create executable
- [] Create repo
- [] Create release
