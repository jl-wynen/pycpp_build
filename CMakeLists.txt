cmake_minimum_required(VERSION 2.8.12)

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_SOURCE_DIR}/cmake/Modules/")

function (target_linker_flags target flags)
  if (flags)
    string(REPLACE ";" " " str_flags "${flags}")
    get_target_property(old ${target} LINK_FLAGS)
    if ("${old}" MATCHES "^.*-NOTFOUND")
      set_target_properties(${target} PROPERTIES LINK_FLAGS "${str_flags}")
    else ()
      set_target_properties(${target} PROPERTIES LINK_FLAGS "${old} ${str_flags}")
    endif ()
  endif ()
endfunction ()

project(python_cpp_example)

set(SOURCE_DIR "src/python_cpp_example")
include_directories(${SOURCE_DIR})
set(SOURCES "${SOURCE_DIR}/math.cpp")

# add_subdirectory(lib/pybind11)
# pybind11_add_module(python_cpp_example ${SOURCES} ${SOURCE_DIR}/bindings.cpp)

add_library(python_cpp_example MODULE ${SOURCES} ${SOURCE_DIR}/bindings.cpp)


# Pybind11
find_package(Pybind11 REQUIRED)
set_target_properties(python_cpp_example PROPERTIES PREFIX "" SUFFIX "${PYBIND11_LIB_SUFFIX}")
include_directories(SYSTEM "${PYBIND11_INCLUDE_DIRS}")
target_compile_options(python_cpp_example PUBLIC ${PYBIND11_CXX_FLAGS})
target_link_libraries(python_cpp_example ${PYBIND11_LIBRARIES})
target_linker_flags(python_cpp_example "${PYBIND11_LINKER_FLAGS}")

# set standard
set_target_properties(python_cpp_example PROPERTIES CXX_STANDARD 14
  CXX_STANDARD_REQUIRED ON)



#### unit tests

set(TEST_DIR "tests")
set(TESTS ${SOURCES}
  "${TEST_DIR}/test_main.cpp"
  "${TEST_DIR}/test_math.cpp")

include_directories(lib/catch/include)
add_executable("${PROJECT_NAME}_test" ${TESTS})
