#include <pybind11/pybind11.h>
#include "math.hpp"

namespace py = pybind11;

PYBIND11_MODULE(python_cpp_example, m) {
    m.def("add", &add);
    m.def("subtract", &subtract);
}
