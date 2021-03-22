# C++ Special Member Functions

**Special member functions** are member functions (of user-defined classes) that are defined by the compiler even if not defined by the user if needed. That is, the compiler generates a default version of them if the user doesn't define them but the code calls it somewhere.
Default implementations for copies are member-wise copies (copy over every member), and moves are member-wise moves (try to move each member, else copy).
The special member functions for a class `Widget` are:

* **Default constructor:** the constructor with no arguments.

	- Definition: `Widget();`

	- Usage: `Widget w();`

* **Copy constructor:** the constructor that takes another `Widget` and makes a copy of it.

	- Definition: `Widget(const Widget&);`

	- Usage: `Widget w1(w);`

* **Copy assignment operator:** setting one `Widget` to equal another `Widget` using the `=` operator.

	- Definition: `Widget& operator=(const Widget&)`

	- Usage: `w1 = w2;`

* **Move constructor:** the constructor that takes an rvalue reference to another `Widget` and constructs a new object by moving it.

	- Definition: `Widget(Widget&& rhs);`

	- Usage: `Widget w3(std::move(w2));`

* **Move assignment operator:** setting one `Widget` to equal another `Widget` using the `=` operator, with moving.

	- Definition: `Widget& operator=(Widget&& rhs)`
	
	- Usage: `w1 = w2;`

* **Destructor:** function that destroys a `Widget` object.

	- Definition: `~Widget();`

	- Usage: `delete widget;`



Table for when special member functions are defined (rows = you declare, columns = compiler defines):

|u👇compiler👉        | Default constructor | Copy constructor | Copy operator= | Move constructor | Move operator= | Destructor |
| ------------------- | ------------------- | ---------------- | -------------- | ---------------- | -------------- | ---------- |
| Nothing             | YES                 | YES              | YES            | YES              | YES            | YES        |
| Default constructor | NO                  | YES              | YES            | YES              | YES            | YES        |
| Copy constructor    | NO                  | NO               | YES            | NO               | NO             | YES        |
| Copy operator=      | YES                 | YES              | NO             | NO               | NO             | YES        |
| Move constructor    | NO                  | DELETED          | DELETED        | NO               | NO             | YES        |
| Move operator=      | YES                 | DELETED          | DELETED        | NO               | NO             | YES        |
| Destructor          | YES                 | YES              | YES            | NO               | NO             | NO         |


Noteworthy:

- The default constructor is only created if you declare no constructors at all.
- If you declare a copy function, the compiler won't create move stuff, because if you can't just do a memberwise copy, then move is probably different too.
- If you declare ANY move function (constructor OR operator=), compiler will delete BOTH copy ones. It doesn't make sense for the compiler to define copy stuff if you made move stuff.
- If you delcare just the copy constructor but not copy operator= or vice versa, the compiler still creates the one you didn't define. But this isn't the case for the move functions, it's both or neither.
- Declaring a destructor means the compiler will not automatically generate move constructor and move operator=, so it can actually impact performance.


"**Rule of Three:**" you should declare all or none of: copy constructor, copy operator=, and destructor.

Taken from _Effective Modern C++_
