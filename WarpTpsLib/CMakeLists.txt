cmake_minimum_required(VERSION 3.15)
project(WarpTpsLib VERSION 1.0.0 LANGUAGES CXX)

# C++ Standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Find Boost
find_package(Boost 1.70 REQUIRED COMPONENTS system)

# Library sources
set(LIBRARY_SOURCES
    ModelObject.cpp
    TPSTransform.cpp
)

# Library headers
set(LIBRARY_HEADERS
    ModelObject.h
    TPSTransform.h
    VectorD.h
    VectorBase.h
    MathUtil.h
    UtilMacros.h
    framework.h
)

# Create library target
add_library(WarpTpsLib STATIC ${LIBRARY_SOURCES} ${LIBRARY_HEADERS})

# Include directories
target_include_directories(WarpTpsLib PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
    $<INSTALL_INTERFACE:include>
)

# Link Boost
target_link_libraries(WarpTpsLib PUBLIC Boost::headers)

# Compiler options
if(MSVC)
    target_compile_options(WarpTpsLib PRIVATE /W3)
else()
    target_compile_options(WarpTpsLib PRIVATE -Wall -Wextra -Wpedantic)
endif()

# Installation rules
install(TARGETS WarpTpsLib
    EXPORT WarpTpsLibTargets
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    RUNTIME DESTINATION bin
    INCLUDES DESTINATION include
)

install(FILES ${LIBRARY_HEADERS}
    DESTINATION include/WarpTpsLib
)

# Export cmake config
install(EXPORT WarpTpsLibTargets
    FILE WarpTpsLibTargets.cmake
    NAMESPACE WarpTps::
    DESTINATION lib/cmake/WarpTpsLib
)
