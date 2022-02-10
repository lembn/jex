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

- [ ] Log compile-time errors, then quit (don't run)
- [ ] Log run-time errors
- [ ] Log to file
- [ ] Create flag for silent/loud
- [ ] Debug mode
  - [ ] Call `jdb` instead of `java`
  - [ ] Debug binaries have to be compiled differently
- [ ] Create executable
  - [ ] Create release

```python
result = subprocess.run(['ls', '-l'], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)
```
