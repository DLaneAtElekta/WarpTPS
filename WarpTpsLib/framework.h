#pragma once

// Cross-platform type definitions
// When MFC is available, use MFC types for compatibility with existing code
// Otherwise, use standard C++ types

#ifdef __AFX_H__
#ifndef VC_EXTRALEAN
#define VC_EXTRALEAN            // Exclude rarely-used stuff from Windows headers
#endif

#define _ATL_CSTRING_EXPLICIT_CONSTRUCTORS      // some CString constructors will be explicit

#include <afxwin.h>         // MFC core and standard components
#else
// Cross-platform includes
#include <cstdint>
#include <cassert>

// Legacy Windows type compatibility (only when not using MFC)
typedef unsigned char BYTE;
typedef BYTE* LPBYTE;

#define ASSERT assert
#endif
