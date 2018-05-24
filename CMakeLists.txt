cmake_minimum_required(VERSION 2.8.12)

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_SOURCE_DIR}/cmake/Modules/")

# verify required arguments are there
set(LIBRARY_NAME "" CACHE STRING "Name of the output library")
if ("${LIBRARY_NAME}" STREQUAL "")
  message(FATAL_ERROR "No library name given")
endif ()

set(TEST_DIR "" CACHE STRING "Directory for unit tests")
if ("${TEST_DIR}" STREQUAL "")
  message(FATAL_ERROR "No test directory given")
endif ()


project(${LIBRARY_NAME} CXX)

get_filename_component(SOURCE_DIR "src/${LIBRARY_NAME}/cpp"
  REALPATH BASE_DIR "${CMAKE_SOURCE_DIR}")
add_subdirectory(${SOURCE_DIR})

get_filename_component(TEST_DIR "tests/cpp"
  REALPATH BASE_DIR "${CMAKE_SOURCE_DIR}")
add_subdirectory(${TEST_DIR})
