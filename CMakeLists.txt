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

set(LIBRARY_NAME "" CACHE STRING "Name of the output library")
if ("${LIBRARY_NAME}" STREQUAL "")
  message(FATAL_ERROR "No library name given")
endif ()

set(TEST_DIR "" CACHE STRING "Directory for unit tests")
if ("${TEST_DIR}" STREQUAL "")
  message(FATAL_ERROR "No test directory given")
endif ()

project(${LIBRARY_NAME})

set(SOURCE_DIR "src/${LIBRARY_NAME}")
include_directories(${SOURCE_DIR})
set(SOURCES "${SOURCE_DIR}/math.cpp")

add_library(${LIBRARY_NAME} MODULE ${SOURCES} ${SOURCE_DIR}/bindings.cpp)


# Pybind11
find_package(Pybind11 REQUIRED)
set_target_properties(${LIBRARY_NAME} PROPERTIES PREFIX "" SUFFIX "${PYBIND11_LIB_SUFFIX}")
include_directories(SYSTEM "${PYBIND11_INCLUDE_DIRS}")
target_compile_options(${LIBRARY_NAME} PUBLIC ${PYBIND11_CXX_FLAGS})
target_link_libraries(${LIBRARY_NAME} ${PYBIND11_LIBRARIES})
target_linker_flags(${LIBRARY_NAME} "${PYBIND11_LINKER_FLAGS}")

# set standard
set_target_properties(${LIBRARY_NAME} PROPERTIES CXX_STANDARD 14
  CXX_STANDARD_REQUIRED ON)



#### unit tests

set(TESTS ${SOURCES}
  "${TEST_DIR}/test_main.cpp"
  "${TEST_DIR}/test_math.cpp")


set(CATCH_INCLUDE "" CACHE STRING "Path to catch")
if (NOT "${CATCH_INCLUDE}" STREQUAL "")
  message(STATUS "Using catch in ${CATCH_INCLUDE}")
  include_directories("${CATCH_INCLUDE}")
else ()
  message(STATUS "Using catch in default path")
endif ()
add_executable("${LIBRARY_NAME}_test" ${TESTS})
install(TARGETS "${LIBRARY_NAME}_test" DESTINATION "${TEST_DIR}/bin")
