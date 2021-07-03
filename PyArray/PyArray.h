#pragma once

#ifdef DEBUG
#define PYARRAY_API __declspec(dllexport)
#else
#define PYARRAY_API __declspec(dllimport)
#endif // DEBUG

