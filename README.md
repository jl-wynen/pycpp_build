# Build Python packages with C++ extensions

This is an example project showing how a Python package using a C++ extension can be
built using `setuptools` + `CMake`.
Includes code to compile, install, build and run unit tests, and build documentation.
It is based on the blog post http://www.benjack.io/2017/06/12/python-cpp-tests.html

## Usage
- *Download* [Catch2](https://github.com/catchorg/Catch2) into `./lib`
- *Configure extension*
  ```
  python setup.py configure --catch=lib/Catch2/single_include
  ```
- *Build extension*
  * For deployment
  ```
  pip install . --user    # or python setup.py install --user
  ```
  * For development
  ```
  pip install -e . --user    # or python setup.py develop --user
  ```
  Afterwards, Python files can be modified without rebuilding, C++ files can be rebuilt
  using `python setup.py build`.
- *Uninstall*
  Simply use `pip uninstall pycpp_build`.
  Note that this tends to leave the script `hei` behind.
- *Test*
  ```
  python setup.py test
  ```
- *Build documentation*
  ```
  python setup.py doc
  ```
  
## For other packages
This is not a Python package meant to be included in other projects.
To use it, simple copy the `setup` folder into your project and write `CMakeLists.txt` files
analogously to the ones in this project and write a proper `setup.py`.

See [isle](https://github.com/jl-wynen/isle) for a real life example. Note that isle uses a slightly adapted version of the code in this repo.

## Limitations
- No Windows support.
- Designed for and tested with only a single extension library.
  No guarantees that it works with more than one.
