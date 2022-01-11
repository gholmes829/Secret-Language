# Secret-Language

Below is a list of intended language features and design

### Language Features and Design
Control:
- Where (y = x + x where x = 2)
- Until (inverse while)
- Unless (inverse if)
- Pattern matching
- In place walrus assignment
- Ternary expr
- Infinite range (better than “int i; while (true) {I++}”
- For else loops
- While else (?)

Scope:
- Context managers
- slightly dynamic scopes (like Python?)

Functional:
- Good anonymous fns (arrow notation esque)
- Map, filter, reduce, for each
- Decorators
- Closures

Classes:
- Inheritance
- Function overloading

Concurrency:
- Go based concurrency
- Anything else??

Types and Builtins:
- List/ dict/ set comprehension
- Type defs
- F string and string formatting
- Built in bin, hex, old, cron, etc
- expr or expr (using truthiness like in Python or JS)
- forward declaration
- Build in support for infinity, negative_inf

General/ High Level:
- More English syntax (is not None)
- Typing w fn def, but not with var decl
- NO If \_\_name__ is main like python, need explicit entry point

Other:
- Pipes and redirection
- Last expression implicit return
- Variable unpacking
- *, ** like in Python
- \_\_debug__ like constant
- dynamic imports (?, may not be feasible if needs typing and whatnot)
- Built in timer functionality (perhaps as context manager?)

Backend:
- consider LLVM and JIT
- unparse to Python (?)

Optimizations:
- constexpr compile time calculation
- const keyword maybe used w sets for example to make hashable frozen sets
- lru caching
- specify if pure (maybe other flags?)
- some sort of specializer (sounds very hard but could be cool?)

Files:
- __init__ files (or is there a better alternative?

Tools:
- Obfuscation tool
- Built in html generation documenter

Meta:
- Make parser state graph

Branding:
- language name
- file extensions
- cool mascot
