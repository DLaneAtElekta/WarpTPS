# WarpTpsLib.UnitTests - Unit tests for WarpTpsLib
project(WarpTpsLibUnitTests VERSION 1.0.0)

# Note: This uses Visual Studio's native unit test framework
# For cross-platform builds, consider migrating to Google Test or Catch2

if(NOT MSVC)
    message(WARNING "Visual Studio native unit tests require MSVC - skipping")
    return()
endif()

# Source files
set(SOURCES
    pch.cpp
    WarpTpsLibTests.cpp
)

# Header files
set(HEADERS
    pch.h
)

# Create test DLL
add_library(WarpTpsLibUnitTests SHARED ${SOURCES} ${HEADERS})

# Set precompiled header
target_precompile_headers(WarpTpsLibUnitTests PRIVATE pch.h)

# Include directories
target_include_directories(WarpTpsLibUnitTests PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_SOURCE_DIR}/WarpTpsLib
    # Visual Studio Unit Test framework headers
    # Note: Path may vary based on VS installation
    "$ENV{VCInstallDir}Auxiliary/VS/UnitTest/include"
)

# Link dependencies
target_link_libraries(WarpTpsLibUnitTests PRIVATE
    WarpTpsLib
    Boost::headers
)

# Link Visual Studio Unit Test framework libraries
# Note: Path may vary based on VS installation
if(CMAKE_SIZEOF_VOID_P EQUAL 8)
    # 64-bit
    target_link_directories(WarpTpsLibUnitTests PRIVATE
        "$ENV{VCInstallDir}Auxiliary/VS/UnitTest/lib"
    )
else()
    # 32-bit
    target_link_directories(WarpTpsLibUnitTests PRIVATE
        "$ENV{VCInstallDir}Auxiliary/VS/UnitTest/lib"
    )
endif()

# Compiler-specific settings
target_compile_definitions(WarpTpsLibUnitTests PRIVATE
    WIN32
    $<$<CONFIG:Debug>:_DEBUG>
    $<$<CONFIG:Release>:NDEBUG>
)

target_compile_options(WarpTpsLibUnitTests PRIVATE
    /W3
    $<$<CONFIG:Release>:/O2>
)

# Set subsystem
set_target_properties(WarpTpsLibUnitTests PROPERTIES
    LINK_FLAGS "/SUBSYSTEM:WINDOWS"
)

# Enable MFC for Win32 builds
if(CMAKE_SIZEOF_VOID_P EQUAL 4)  # 32-bit
    set_target_properties(WarpTpsLibUnitTests PROPERTIES
        MFC_FLAG 2  # Shared MFC
    )
endif()

# Enable testing
enable_testing()

# Add test (note: requires vstest.console.exe for execution)
add_test(
    NAME WarpTpsLibUnitTests
    COMMAND vstest.console.exe $<TARGET_FILE:WarpTpsLibUnitTests>
)

message(STATUS "WarpTpsLib unit tests configured (Visual Studio native unit tests)")
