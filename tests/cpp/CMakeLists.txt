set(TEST_SOURCES
  ${LIBRARY_SOURCES}
  "test_main.cpp"
  "test_math.cpp")

set(TEST_EXE "${LIBRARY_NAME}_test")

add_executable(${TEST_EXE} ${TEST_SOURCES})
target_include_directories(${TEST_EXE} PUBLIC ${SOURCE_DIR})
install(TARGETS "${LIBRARY_NAME}_test" DESTINATION "${TEST_DIR}/../bin")

set(CATCH_INCLUDE "" CACHE STRING "Path to catch")
if (NOT "${CATCH_INCLUDE}" STREQUAL "")
  message(STATUS "Using catch in ${CATCH_INCLUDE}")
  get_filename_component(catch_dir "${CATCH_INCLUDE}"
    REALPATH BASE_DIR "${CMAKE_SOURCE_DIR}")
  target_include_directories(${TEST_EXE} SYSTEM PUBLIC "${catch_dir}")
  unset(catch_dir)
else ()
  message(STATUS "Using catch in default path")
endif ()
