# Build

<!--
Hello fanquake, this is what we dummies are like: We usually have a magic Makefile that someone
wrote beforehand, we run `make`, and then magically everything works. If something goes wrong or
we're just curious, we might try to read the Makefile, but we have no idea what's going on, so we
cry and wait for someone to help us.

A dummy reads this because
- curiousity: they don't know what build systems are and don't wanna sound stupid
- future troubleshooting: this might give them some intuition for how to help themselves when
  something goes wrong. they might have an idea of what to ignore and what not to ignore.
-->

Q: What is the point of the build system:

1. Build stuff for humans: Go from source code to executable in a few commands.

2. Be Interoperable: For the purpose of accessibility and just general software
   compatibility, Bitcoin Core is supposed to run on various hardware, [operating
systems](https://github.com/fanquake/core-review/blob/master/operating-systems.md), configurations,
etc. Preferrably, this works without requiring a ton of custom-written code or significant reduction in
performance. This looks and sounds like magic, but isn't.


```
   ____     _   _             _      ____         ____      __   __ ____     _____  U _____ u  __  __    ____
U | __")uU |"|u| |   ___     |"|    |  _"\       / __"| u   \ \ / // __"| u |_ " _| \| ___"|/U|' \/ '|u / __"| u
 \|  _ \/ \| |\| |  |_"_|  U | | u /| | | |     <\___ \/     \ V /<\___ \/    | |    |  _|"  \| |\/| |/<\___ \/
  | |_) |  | |_| |   | |    \| |/__U| |_| |\     u___) |    U_|"|_uu___) |   /| |\   | |___   | |  | |  u___) |
  |____/  <<\___/  U/| |\u   |_____||____/ u     |____/>>     |_|  |____/>> u |_|U   |_____|  |_|  |_|  |____/>>
 _|| \\_ (__) )(.-,_|___|_,-.//  \\  |||_         )(  (__).-,//|(_  )(  (__)_// \\_  <<   >> <<,-,,-.    )(  (__)
(__) (__)    (__)\_)-' '-(_/(_")("_)(__)_)       (__)      \_) (__)(__)    (__) (__)(__) (__) (./  \.)  (__)
```

## General Concepts not specific to Bitcoin Core

### How do I get from source files to binary

Conceptually, the Makefile defines a bunch of build targets and internal/external dependencies.
This gives us a DAG of build targets, (e.g. you need stdlib to build validation.h and you need
validation.h to build bitcoind) and `make` figures out how to do everything in order to get the
result you want.

1. Should have compiler and dependencies
2. Preprocessing
3. Compiling
4. Assembling
5. Linking
6. Loading

Read more:
- http://oberon00.github.io/cpptutorial/proc/hello-world.html
- https://cs61c.org/sp21/lectures/?file=lec09_call.key.pdf


### Definitions

Terms that are non-obvious to dummies

- Toolchain
- host vs native, cross compilation
- Proper nouns


## General Bitcoin Core Build stuff?

Q: What falls under the build systems umbrella in Bitcoin

- code-wise
- functionality-wise

Q: What are these files and directories:

- autogen.sh
- configure.ac
- configure
- config.log
- Makefile.am
- Makefile.in
- Makefile
- libbitcoinconsensus.pc.in
- build-aux/
- build_msvc/
- depends/

Q: What's the difference between subtrees (minisketch, univalue, libsecp256) dnd depends (qt, boost)

Q: Overall goals of build system work

- It should become more \_, less \_
- Ideally, we have \_
- Security-wise, \_ is a problem
- PRs that are nice examples include \_

## Building

### GNU uhhhhhh... stuff

./autogen.sh

What it does:

How it does this:

How do I read the output:

./configure

What it does: In general, this is supposed to gather information about your system.

How it does this: Autotools

How do I read the output: When `./configure` is running, it prints the action it's doing... and then the result.

make

What happens when you run ./configure

What it does:

How it does this:

How do I read the output: When `make` is running, it prints the target it's currently building (I think).

### not... GNU...?

???
????????


Q: If I add a file to the source code, what should I modify in the Makefiles

