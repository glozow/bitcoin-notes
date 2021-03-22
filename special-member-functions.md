# C++ Special Member Functions

**Special member functions** are member functions (of user-defined classes) that are defined by the compiler even if not defined by the user if needed. That is, the compiler generates a default version of them if the user doesn't define them but the code calls it somewhere.
The special member functions for a class `Widget` are:

* **Default constructor:** the constructor with no arguments

	- Definition: `Widget();`

	- Usage: `Widget w();`

* **Copy constructor:** the constructor that takes another `Widget` and makes a copy of it

	- Definition: `Widget(const Widget&);`

	- Usage: `Widget w1(w);`

* **Copy assignment operator:** setting one `Widget` to equal another `Widget` using the `=` operator

	- Definition: `Widget& operator=(const Widget&)`

	- Usage: `w1 = w2;`

* **Move constructor:** the constructor that takes an rvalue reference to another `Widget` and constructs a new object by moving it

	- Definition: `Widget(Widget&& rhs);`

	- Usage: `Widget w3(std::move(w2));`

* **Move assignment operator:** setting one `Widget` to equal another `Widget` using the `=` operator, with move semantics

	- Definition: `Widget& operator=(Widget&& rhs)`
	
	- Usage: `w1 = w2;`

* **Destructor:** function that destroys a `Widget` object

	- Definition: `~Widget();`

	- Usage: `delete widget;`
