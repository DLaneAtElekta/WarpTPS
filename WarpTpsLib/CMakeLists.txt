cmake_minimum_required(VERSION 3.15)
project(WarpTpsLib VERSION 1.0.0 LANGUAGES CXX)

# C++ Standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Options
option(USE_MFC "Build with MFC support (Windows only)" OFF)
option(BUILD_SHARED_LIBS "Build shared library instead of static" OFF)

# Find Boost
find_package(Boost 1.70 REQUIRED COMPONENTS system)

# Library sources - cross-platform core
set(LIBRARY_SOURCES
    ModelObject.cpp
    TPSTransform.cpp
)

# Library headers - cross-platform core
set(LIBRARY_HEADERS
    ModelObject.h
    TPSTransform.h
    VectorD.h
    VectorBase.h
    MathUtil.h
    UtilMacros.h
    framework.h
)

# Add MFC-specific files if enabled
if(USE_MFC AND MSVC)
    list(APPEND LIBRARY_SOURCES pch.cpp)
    list(APPEND LIBRARY_HEADERS
        pch.h
        Resource.h
        targetver.h
    )
    set(RESOURCES
        WarpTpsLib.rc
        res/WarpTpsLib.rc2
    )
endif()

# Create library target
if(BUILD_SHARED_LIBS)
    if(USE_MFC AND MSVC)
        add_library(WarpTpsLib SHARED ${LIBRARY_SOURCES} ${LIBRARY_HEADERS} ${RESOURCES})
        
        # Add DLL export definitions
        target_compile_definitions(WarpTpsLib PRIVATE
            WARPTPSLIB_EXPORTS
            _USRDLL
        )
        
        # Use module definition file for exports
        set_target_properties(WarpTpsLib PROPERTIES
            LINK_FLAGS "/DEF:${CMAKE_CURRENT_SOURCE_DIR}/WarpTpsLib.def"
        )
    else()
        add_library(WarpTpsLib SHARED ${LIBRARY_SOURCES} ${LIBRARY_HEADERS})
    endif()
else()
    if(USE_MFC AND MSVC)
        add_library(WarpTpsLib STATIC ${LIBRARY_SOURCES} ${LIBRARY_HEADERS} ${RESOURCES})
    else()
        add_library(WarpTpsLib STATIC ${LIBRARY_SOURCES} ${LIBRARY_HEADERS})
    endif()
endif()

# Set precompiled header for MFC builds
if(USE_MFC AND MSVC)
    target_precompile_headers(WarpTpsLib PRIVATE pch.h)
endif()

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
    
    # MFC-specific compiler settings
    if(USE_MFC)
        target_compile_definitions(WarpTpsLib PRIVATE
            WIN32
            _WINDOWS
            $<$<CONFIG:Debug>:_DEBUG>
            $<$<CONFIG:Release>:NDEBUG>
        )
        
        target_compile_options(WarpTpsLib PRIVATE
            $<$<CONFIG:Release>:/O2>
            /permissive  # Disable conformance mode for MFC compatibility
        )
    endif()
else()
    target_compile_options(WarpTpsLib PRIVATE -Wall -Wextra -Wpedantic)
endif()

# Set target properties
set_target_properties(WarpTpsLib PROPERTIES
    OUTPUT_NAME "WarpTpsLib"
    VERSION ${PROJECT_VERSION}
)

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

# ============================================================================
# Python bindings with pybind11
# ============================================================================
option(BUILD_PYTHON_BINDINGS "Build Python bindings with pybind11" OFF)

if(BUILD_PYTHON_BINDINGS)
    message(STATUS "Building Python bindings")

    # Find Python
    find_package(Python COMPONENTS Interpreter Development REQUIRED)
    message(STATUS "Python version: ${Python_VERSION}")
    message(STATUS "Python include dirs: ${Python_INCLUDE_DIRS}")

    # Find pybind11
    find_package(pybind11 CONFIG REQUIRED)
    message(STATUS "pybind11 version: ${pybind11_VERSION}")

    # Create Python bindings module
    pybind11_add_module(_warptps_core
        python/bindings.cpp
    )

    # Link against WarpTpsLib
    target_link_libraries(_warptps_core PRIVATE WarpTpsLib)

    # Set output name and properties
    set_target_properties(_warptps_core PROPERTIES
        OUTPUT_NAME "_warptps_core"
        CXX_VISIBILITY_PRESET "hidden"
        VISIBILITY_INLINES_HIDDEN ON
    )

    # Install the Python module
    install(TARGETS _warptps_core
        LIBRARY DESTINATION warptps
        RUNTIME DESTINATION warptps
    )
endif()
