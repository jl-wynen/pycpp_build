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


set(SOURCES math.cpp)

# need to keep bindings out of this
set(libsrc)
foreach (src IN LISTS SOURCES)
  list(APPEND libsrc "${CMAKE_CURRENT_LIST_DIR}/${src}")
endforeach ()
set(LIBRARY_SOURCES ${libsrc} PARENT_SCOPE)
unset(libsrc)

add_library(${LIBRARY_NAME} SHARED ${SOURCES} bindings.cpp)

# Pybind11
find_package(Pybind11 REQUIRED)
set_target_properties(${LIBRARY_NAME} PROPERTIES PREFIX "" SUFFIX "${PYBIND11_LIB_SUFFIX}")
target_include_directories(${LIBRARY_NAME} SYSTEM PUBLIC "${PYBIND11_INCLUDE_DIRS}")
target_compile_options(${LIBRARY_NAME} PUBLIC ${PYBIND11_CXX_FLAGS})
target_link_libraries(${LIBRARY_NAME} ${PYBIND11_LIBRARIES})
target_linker_flags(${LIBRARY_NAME} "${PYBIND11_LINKER_FLAGS}")

# set standard
set_target_properties(${LIBRARY_NAME} PROPERTIES CXX_STANDARD 14
  CXX_STANDARD_REQUIRED ON)
