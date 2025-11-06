msbuild /p:Configuration=Debug /p:Platform=x86
msbuild /p:Configuration=Release /p:Platform=x86

vstest.console.exe Debug\WarpTpsLib.UnitTests.dll
vstest.console.exe Release\WarpTpsLib.UnitTests.dll