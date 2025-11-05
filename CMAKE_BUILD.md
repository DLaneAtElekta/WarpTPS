# CMake Build Instructions for WarpTPS

This document describes how to build WarpTPS using CMake.

## Platform Support

### Component Availability by Platform

| Component | Windows | Linux | macOS |
|-----------|---------|-------|-------|
| WarpTpsLib (Core Library) | ✅ | ✅ | ✅ |
| Python Bindings | ✅ | ✅ | ✅ |
| WarpWebServer | ✅ | ⚠️* | ⚠️* |
| FeatureExtractionConsole | ✅ | ✅** | ✅** |
| WarpTPS MFC GUI | ✅ | ❌ | ❌ |
| Unit Tests | ✅ | ❌*** | ❌*** |

*WarpWebServer requires libpng and zlib (not currently configured for Linux/macOS)  
**FeatureExtractionConsole requires OpenCV  
***Unit tests use Visual Studio native test framework (MSVC only)

## Prerequisites

### Required
- CMake 3.15 or higher
- C++17 compatible compiler
- Boost 1.87.0 or compatible version

### Platform-Specific Requirements

#### Windows
- Visual Studio 2019 or 2022 (for MFC support)
- Windows SDK 10.0

#### Linux/macOS
- GCC 7+ or Clang 5+
- Note: MFC application will not build on non-Windows platforms

### Optional Dependencies
- **OpenCV**: Required for FeatureExtractionConsole
- **libpng**: Optional for WarpWebServer
- **ZLIB**: Optional for WarpWebServer

## Project Structure

The WarpTPS project consists of several components:

1. **WarpTpsLib**: Core TPS transform library (static/shared library)
2. **WarpWebServer**: HTTP server application using Boost.Asio
3. **FeatureExtractionConsole**: OpenCV-based feature extraction tool
4. **WarpTPS**: Main MFC GUI application (Windows only)
5. **WarpTpsLibUnitTest**: Unit tests using Visual Studio test framework

## Building with CMake

### Basic Build (Windows)

```bash
# Restore NuGet packages first
nuget restore packages.config -PackagesDirectory packages

# Create build directory
mkdir build
cd build

# Configure (Visual Studio)
cmake .. -G "Visual Studio 17 2022" -A Win32 -DUSE_MFC=ON

# Or for 64-bit
cmake .. -G "Visual Studio 17 2022" -A x64 -DUSE_MFC=ON

# Build
cmake --build . --config Release

# Or open the generated solution in Visual Studio
start WarpTPS.sln
```

### Build with Specific Options

```bash
# Build shared libraries instead of static
cmake .. -DBUILD_SHARED_LIBS=ON

# Disable MFC application
cmake .. -DUSE_MFC=OFF

# Specify Boost location (if not found automatically)
cmake .. -DBOOST_ROOT=C:/path/to/boost_1_87_0

# Specify OpenCV location
cmake .. -DOpenCV_DIR=C:/path/to/opencv/build
```

### Build Types

```bash
# Debug build
cmake --build . --config Debug

# Release build
cmake --build . --config Release
```

## Linux/macOS Build

WarpTpsLib and its Python bindings are now fully supported on Linux and macOS.

### Prerequisites

**All Platforms:**
- CMake 3.15 or higher
- C++17 compatible compiler (GCC 7+, Clang 5+, or AppleClang)
- Boost 1.70 or higher

**For Python Bindings:**
- Python 3.8 or higher
- pybind11 2.13 or higher
- NumPy 1.20 or higher

**Note:** Consider using a virtual environment for Python development:
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows
```

### Installing Dependencies

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y \
    cmake \
    g++ \
    libboost-dev \
    libboost-system-dev \
    libboost-date-time-dev \
    libboost-regex-dev \
    python3-dev \
    python3-pip

# Install Python dependencies
pip3 install pybind11 numpy scikit-build-core
```

#### macOS (Homebrew)
```bash
brew install cmake boost python@3.12

# Install Python dependencies
pip3 install pybind11 numpy scikit-build-core
```

#### Fedora/RHEL
```bash
sudo dnf install -y \
    cmake \
    gcc-c++ \
    boost-devel \
    python3-devel \
    python3-pip

# Install Python dependencies
pip3 install pybind11 numpy scikit-build-core
```

### Building WarpTpsLib

```bash
# Create build directory
mkdir build
cd build

# Configure (will skip MFC application and other Windows-only components)
cmake .. -DCMAKE_BUILD_TYPE=Release

# Build
cmake --build . -j$(nproc)  # Linux
cmake --build . -j$(sysctl -n hw.ncpu)  # macOS
```

The build will produce:
- `build/lib/libWarpTpsLib.a` - Static library

### Building with Python Bindings

To build the Python bindings, you need to specify the pybind11 path:

```bash
# Find pybind11 CMake directory
PYBIND11_DIR=$(python3 -m pybind11 --cmakedir)

# Create build directory
mkdir build
cd build

# Configure with Python bindings enabled
cmake .. \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_PYTHON_BINDINGS=ON \
    -Dpybind11_DIR=$PYBIND11_DIR

# Build
cmake --build . -j$(nproc)  # Linux
cmake --build . -j$(sysctl -n hw.ncpu)  # macOS
```

This will produce:
- `build/lib/libWarpTpsLib.a` - Static library
- `build/lib/_warptps_core.*.so` - Python extension module (Linux)
- `build/lib/_warptps_core.*.dylib` - Python extension module (macOS)

### Installing Python Package

#### Option 1: Install from Source (Development)

```bash
# Install in development mode (editable install)
pip3 install -e .
```

This uses scikit-build-core to automatically configure CMake and build the extension.

#### Option 2: Build Wheel

```bash
# Build a wheel package
pip3 install build
python3 -m build

# Install the wheel
pip3 install dist/warptps-1.0.0-*.whl
```

#### Option 3: Manual Install (if using CMake directly)

```bash
# After building with CMake (as shown above), copy the module
cp build/lib/_warptps_core.*.so python/warptps/  # Linux
cp build/lib/_warptps_core.*.dylib python/warptps/  # macOS

# Add to Python path or install
export PYTHONPATH=/path/to/WarpTPS/python:$PYTHONPATH
```

### Testing Python Bindings

```bash
python3 -c "
import warptps
import numpy as np

# Create a TPS transform
tps = warptps.TPSTransform()
print(f'Version: {warptps.version()}')

# Add landmarks
tps.add_landmark_tuple((100, 100), (110, 110))
tps.add_landmark_tuple((200, 100), (210, 120))
tps.add_landmark_tuple((150, 200), (155, 205))

# Warp an image
img = np.zeros((300, 300, 3), dtype=np.uint8)
warped = tps.warp(img, percent=1.0)
print(f'Success! Warped image shape: {warped.shape}')
"
```

## Running Tests

```bash
# After building, run tests with CTest
ctest -C Release
```

Note: Unit tests use Visual Studio's native test framework and require `vstest.console.exe` to run.

## Installing

```bash
# Install to default location (requires admin/root)
cmake --install . --config Release

# Install to custom location
cmake --install . --prefix /path/to/install --config Release
```

## Component Selection

You can disable specific components by editing the root `CMakeLists.txt` or by not including their subdirectories.

### Disabling Components

Comment out unwanted components in the root `CMakeLists.txt`:

```cmake
# add_subdirectory(WarpWebServer)  # Disable web server
# add_subdirectory(FeatureExtractionConsole)  # Disable if no OpenCV
```

## Troubleshooting

### Boost Not Found

If CMake cannot find Boost:

1. Ensure NuGet packages are restored:
   ```bash
   nuget restore packages.config -PackagesDirectory packages
   ```

2. Verify the `packages/` directory contains:
   - `boost.1.87.0/`
   - `boost_date_time-vc142.1.87.0/`
   - `boost_regex-vc142.1.87.0/`

3. CMake uses the custom `cmake/FindBoostNuGet.cmake` module which looks for packages in the `packages/` directory

### OpenCV Not Found

If you don't have OpenCV or don't need FeatureExtractionConsole:

```bash
# OpenCV is optional; FeatureExtractionConsole will be skipped if not found
cmake ..
```

To specify OpenCV location:

```bash
cmake .. -DOpenCV_DIR=C:/opencv/build
```

### MFC Not Available

On non-Windows systems or if MFC is not installed:

- The WarpTPS MFC application will be automatically skipped
- All other components will still build

### Visual Studio Unit Tests

Unit tests require Visual Studio's native test framework:

- Only available with MSVC compiler
- Requires Visual Studio installation
- Tests run using `vstest.console.exe`

## Build Output

Built executables and libraries will be placed in:
- `build/bin/` - Executables
- `build/lib/` - Libraries

## Migration Notes

### From MSBuild to CMake

The CMake build system is designed to coexist with the existing MSBuild (`.vcxproj`) files:

- All source files remain in their original locations
- CMake uses the same preprocessor definitions and compiler flags
- Both build systems can be used interchangeably

### Key Differences

1. **NuGet Packages**: CMake uses `find_package()` instead of NuGet. You'll need to install dependencies separately.

2. **Precompiled Headers**: CMake uses `target_precompile_headers()` which may behave slightly differently than Visual Studio's PCH.

3. **MFC**: CMake's MFC support requires setting `MFC_FLAG` property on targets.

4. **Output Directories**: CMake uses `build/bin` and `build/lib` instead of `Debug/` and `Release/`.

## Additional Resources

- [CMake Documentation](https://cmake.org/documentation/)
- [Boost Getting Started](https://www.boost.org/doc/libs/1_87_0/more/getting_started/)
- [OpenCV Installation Guide](https://docs.opencv.org/master/df/d65/tutorial_table_of_content_introduction.html)

## Support

For issues with the CMake build system, please check:
1. CMake version is 3.15+
2. All required dependencies are installed
3. Compiler is C++17 compatible
4. Boost version is 1.87.0 or compatible
