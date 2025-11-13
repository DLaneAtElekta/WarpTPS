@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Building C++ Projects
echo ========================================

msbuild /p:Configuration=Debug /p:Platform=x86
if !ERRORLEVEL! neq 0 (
    echo C++ Debug build failed
    exit /b !ERRORLEVEL!
)

msbuild /p:Configuration=Release /p:Platform=x86
if !ERRORLEVEL! neq 0 (
    echo C++ Release build failed
    exit /b !ERRORLEVEL!
)

echo ========================================
echo Running C++ Unit Tests
echo ========================================

vstest.console.exe Debug\WarpTpsLib.UnitTests.dll
if !ERRORLEVEL! neq 0 (
    echo C++ Debug tests failed
    exit /b !ERRORLEVEL!
)

vstest.console.exe Release\WarpTpsLib.UnitTests.dll
if !ERRORLEVEL! neq 0 (
    echo C++ Release tests failed
    exit /b !ERRORLEVEL!
)

echo ========================================
echo Building Python Package
echo ========================================

python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
if !ERRORLEVEL! neq 0 (
    echo Python package installation failed
    exit /b !ERRORLEVEL!
)

echo ========================================
echo Running Python Unit Tests
echo ========================================

pytest tests/ -v --tb=short
if !ERRORLEVEL! neq 0 (
    echo Python tests failed
    exit /b !ERRORLEVEL!
)

echo ========================================
echo All builds and tests completed successfully
echo ========================================
exit /b 0